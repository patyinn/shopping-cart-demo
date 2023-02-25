import requests
import datetime
import os
import json
import pandas as pd

from requests.auth import HTTPBasicAuth

from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# https://www.learncodewithmike.com/2020/05/django-send-email.html
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

from .token import Token
from .models import MomPlantModel, ChildPlantModel, ChildImageModel, CustomerModel, TransactionModel, OrderModel, Account
from .forms import CustomerModelForm, TranscationModelForm, RegisterModelForm, LoginModelForm
from cart_api.views import CartList

DOMAIN = "http://localhost:8000"

# Create your views here.
def _call_get_cart_api(request):
    if request.user.is_authenticated:
        auth = HTTPBasicAuth(request.user.username, request.user.password)
        response = requests.get(
            DOMAIN + "/api/cart",
            cookies=request.COOKIES,
            auth=auth
        )
    else:
        response = requests.get(
            DOMAIN + "/api/cart",
            cookies=request.COOKIES,
        )
    cart_obj = json.loads(response.content)

    username = response.cookies.get("cart_username")
    token = response.cookies.get(settings.CART_KEY)
    return cart_obj, username, token


def index(request):
    plant_obj = MomPlantModel.objects.all()

    cart_obj, username, token = _call_get_cart_api(request)

    context = {
        'plant_object': plant_obj,
        "Cart_nums": len(cart_obj) if isinstance(cart_obj, list) else 0
    }

    response = render(request, 'index.html', context)
    if username:
        response.set_cookie("cart_username", username)
    if token:
        response.set_cookie(settings.CART_KEY, token)
    return response


def category_page(request, mom):
    mom_plant = MomPlantModel.objects
    plant = ChildPlantModel.objects.filter(category=mom)

    response = requests.get(DOMAIN+"/api/cart")
    cart_obj = json.loads(response.content)

    image = []
    for i in plant:
        image.append(list(ChildImageModel.objects.filter(name=i)))

    cart_obj, username, token = _call_get_cart_api(request)

    context = {
        'plant_object': mom_plant,
        'item': plant,
        # https://bootstrap5.hexschool.com/docs/5.0/components/carousel/#how-it-works
        # https://blog.csdn.net/qq_44302282/article/details/108326844
        # 輪播插件
        'images': image,
        "Cart_nums": len(cart_obj) if isinstance(cart_obj, list) else 0
    }

    response = render(request, 'plants/category.html', context)
    if username:
        response.set_cookie("cart_username", username)
    if token:
        response.set_cookie(settings.CART_KEY, token)
    return response


def plant_page(request, child):
    mom_plant = MomPlantModel.objects
    plant_detail = get_object_or_404(ChildPlantModel, name=child)
    plant_image = ChildImageModel.objects.get(name=child)
    mom = plant_detail.category
    plant = ChildPlantModel.objects.all().filter(category=mom)
    image_list = [i for i in vars(plant_image).values()][3:]
    image_list = [os.path.join('/media', str(i)) for i in image_list if i != '']
    image_list.insert(0, plant_detail.main_image.url)

    cart_obj, username, token = _call_get_cart_api(request)

    context = {
        'plant_object': mom_plant,
        'item': plant,
        'details': plant_detail,
        'images': image_list,
        "Cart_nums": len(cart_obj) if isinstance(cart_obj, list) else 0
    }

    response = render(request, 'plants/detail.html', context)
    if username:
        response.set_cookie("cart_username", username)
    if token:
        response.set_cookie(settings.CART_KEY, token)
    return response


def add_to_cart(request, product):
    headers = {
        'X-CSRFToken': get_token(request),
    }
    product = ChildPlantModel.objects.get(name=product)
    post_data = {
        "product_id": product.id,
        "product_name": product.name,
        "price": product.price,
        "inventory": product.inventory,
        "class_name": product._meta.model_name,
        "app_name": product._meta.app_label,
        "quantity": 1,
        "valid": True,
    }
    if product.sale_price is not None:
        post_data["sale_price"] = product.sale_price

    if request.user.is_authenticated:
        auth = HTTPBasicAuth(request.user.username, request.user.password)
        response = requests.post(
            DOMAIN+"/api/cart/",
            cookies=request.COOKIES,
            json=post_data,
            auth=auth,
            headers=headers,
        )
    else:
        requests.post(
            DOMAIN+"/api/cart/",
            cookies=request.COOKIES,
            json=post_data,
            headers=headers,
        )

    return redirect('/Entry/{}'.format(product))


def remove_from_cart(request, item_pk):
    if request.user.is_authenticated:
        auth = HTTPBasicAuth(request.user.username, request.user.password)
        requests.delete(
            DOMAIN + f"/api/cart/{item_pk}",
            cookies=request.COOKIES,
            auth=auth
        )
    else:
        requests.delete(
            DOMAIN + f"/api/cart/{item_pk}",
            cookies=request.COOKIES,
        )

    return redirect('/Cart')


def update_cart(request, product, item_pk):
    if 'update' in request.POST:
        product = ChildPlantModel.objects.get(name=product)

        qty = request.POST["qty"]
        data = {
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "inventory": product.inventory,
            "class_name": product._meta.model_name,
            "app_name": product._meta.app_label,
            "quantity": qty,
            "valid": True,
        }

        if request.user.is_authenticated:
            auth = HTTPBasicAuth(request.user.username, request.user.password)
            requests.put(
                DOMAIN + f"/api/cart/{item_pk}",
                cookies=request.COOKIES,
                data=data,
                auth=auth
            )
        else:
            requests.put(
                DOMAIN + f"/api/cart/{item_pk}",
                cookies=request.COOKIES,
                data=data,
            )

        return redirect('/Cart')
    else:
        pass


# https://stackoverflow.com/questions/64915167/how-do-i-use-a-django-url-inside-of-an-option-tag-in-a-dropdown-menu
def get_cart(request):
    cart_obj, username, token = _call_get_cart_api(request)
    print(cart_obj)
    if isinstance(cart_obj, list):
        total_price = 0
        for obj in cart_obj:
            obj["product"]["inventory"] = range(obj["product"]["inventory"])
            product_img = ChildPlantModel.objects.get(pk=obj["product"]["product_id"])
            obj["product"]["main_image"] = product_img.main_image
            price = obj["product"]["sale_price"] if obj["product"]["sale_price"] else obj["product"]["price"]
            obj["price"] = obj["quantity"] * price
            total_price += obj["price"]
    else:
        cart_obj = ""
    context = {
        "cart": cart_obj,
        "total_price": total_price
    }

    response = render(request, 'shopping/cart.html', context)
    if username:
        response.set_cookie("cart_username", username)
    if token:
        response.set_cookie(settings.CART_KEY, token)
    return response


# @login_required(login_url="Login")
def order_page(request):
    mom_plant = MomPlantModel.objects
    plant_inventory = ChildPlantModel.objects
    Customer_form = CustomerModelForm()
    Transcation_form = TranscationModelForm()

    if CustomerModel.objects.filter(username=request.user.username).exists():
        saved_customer = CustomerModel.objects.filter(username=request.user.username)
        saved_payment =[]
        for q in saved_customer:
            data = TransactionModel.objects.select_related('customer').filter(customer_id=q, show_info=True)\
                .values('customer__customer', 'customer__email', 'customer__tel', 'customer_id', 'address', 'delivery')\
                .order_by('-delivery').distinct()
            if data:
                saved_payment.append(data)

        if not saved_payment:
            saved_info = '無儲存紀錄'
        else:
            saved_info = saved_payment
    else:
        saved_info = "無儲存紀錄"

    if 'take' in request.POST and request.user.is_authenticated:
        id = request.POST["Submit"]
        customer_id, address, delivery = id.split('/')
        if CustomerModel.objects.filter(username=request.user.username).exists():
            target_customer = CustomerModel.objects.get(username=request.user.username, pk=customer_id)

            if TransactionModel.objects.filter(customer=target_customer).exists():
                target_trans = TransactionModel.objects.filter(customer=target_customer, address=address, delivery=delivery)

                if 'delete_trans' in request.POST:
                    target_trans.update(show_info=False)
                    return redirect('/Order')
                else:
                    target_trans = target_trans.last()
                    Customer_form.fields['customer'].initial = target_customer.customer
                    Customer_form.fields['email'].initial = target_customer.email
                    Customer_form.fields['tel'].initial = target_customer.tel
                    Transcation_form.fields['address'].initial = target_trans.address
                    Transcation_form.fields['delivery'].initial = target_trans.delivery
                    Transcation_form.fields['payment'].initial = target_trans.payment

    # 取得從購物車中確認的購買資料
    Cart_data = pd.DataFrame()
    Cart_list, username, token = _call_get_cart_api(request)
    for item in Cart_list:
        Cart_data = Cart_data.append({
            "id": item["id"],
            'name': item["product"]["product_name"],
            'price': item["product"]["price"],
            'quantity': item["product"]["quantity"],
            'total_price': int(item["product"]["quantity"])*float(item["product"]["price"]),
        }, ignore_index=True)
    try:
        Cart_data = Cart_data.set_index(['name'])
    except:
        messages.warning(request, "出狀況，請重新再執行一次")
        return redirect('Cart')

    if 'purchase' in request.POST:
        form1 = CustomerModelForm(request.POST)
        form2 = CustomerModelForm(request.POST)
        global check_ok
        # 逐一檢查商品狀態與數量是否符合存貨
        for index in range(len(Cart_data)):
            prod = Cart_data.loc[index, 'name']
            inv = plant_inventory.get(name=prod).inventory
            status = plant_inventory.get(name=prod).status
            qty = int(Cart_data.loc[prod, "quantity"])

            if inv >= qty and status == "I":
                check_ok = True
            else:
                check_ok = False
                product = plant_inventory.get(name=prod)
                remove_from_cart(request, Cart_data.loc[index, 'id'])
                break

        if check_ok:
            if form1.is_valid() and form2.is_valid():

                # 新增客戶資料至客戶系統模型上
                customer = request.POST["customer"]
                email = request.POST["email"]
                tel = request.POST["tel"]

                if request.user.is_authenticated:
                    username = request.user.username
                    if not CustomerModel.objects.filter(customer=customer, email=email, tel=tel, username=username).exists():
                        # 新增客戶資料至客戶系統模型上
                        CustomerModel.objects.create(
                            customer=customer,
                            tel=tel,
                            email=email,
                            username=username
                        )
                    else:
                        pass
                else:
                    if not CustomerModel.objects.filter(customer=customer, email=email, tel=tel).exists():
                        CustomerModel.objects.create(
                            customer=customer,
                            tel=tel,
                            email=email
                        )
                # 新增訂單資訊至交易系統模型上
                deal_date = datetime.datetime.now()
                OrderID = datetime.datetime.strftime(deal_date, "%Y%m%d%H%M%S")
                # customer_fk = CustomerModel.objects.only('customer').get(customer=customer)
                if username is not None:
                    customer_fk = CustomerModel.objects.only("id").get(customer=customer, email=email, tel=tel, username=username)
                else:
                    customer_fk = CustomerModel.objects.only("id").get(customer=customer)
                payment = request.POST["payment"]
                delivery = request.POST["delivery"]
                address = request.POST["address"]
                comment = request.POST["comment"]
                if delivery == "S":
                    shipping_fee = 60
                elif delivery == "P":
                    shipping_fee = 80
                else:
                    shipping_fee = 0
                total_payment = Cart_list.summary() + shipping_fee

                if 'save_trans' in request.POST and request.user.is_authenticated:
                    save_check = True
                else:
                    save_check = False


                TransactionModel.objects.create(
                    OrderID=OrderID,
                    customer=customer_fk,
                    payment=payment,
                    delivery=delivery,
                    address=address,
                    comment=comment,
                    shipping_fee=shipping_fee,
                    total_payment=total_payment,
                    deal_date=deal_date,
                    show_info=save_check
                )

                # 新增訂單詳細內容至訂單系統模型上
                for index in range(len(Cart_data)):
                    prod = Cart_data.loc[index, 'name']

                    orderid_fk = TransactionModel.objects.only('OrderID').get(OrderID=OrderID)
                    product_fk = ChildPlantModel.objects.only('name').get(name=prod)
                    price = Cart_data.loc[prod, "price"]
                    qty = Cart_data.loc[prod, "quantity"]
                    total_price = Cart_data.loc[prod, "total_price"]

                    OrderModel.objects.create(
                        OrderID=orderid_fk,
                        product=product_fk,
                        price=price,
                        qty=qty,
                        total_price=total_price
                    )

                    # 修改植物模型的狀態以及訂購完成的存貨數量
                    inv = plant_inventory.get(name=prod).inventory
                    inv -= int(qty)
                    ChildPlantModel.objects.filter(name=prod).update(inventory=inv)
                    if inv == 0:
                        ChildPlantModel.objects.filter(name=prod).update(status="O")

                    remove_from_cart(request, Cart_data.loc[index, 'id'])
                return redirect('/OrderComplete/{}'.format(OrderID))

    cart_obj, username, token = _call_get_cart_api(request)

    context = {
        'plant_object': mom_plant,
        'saved_info': saved_info,
        'form1': Customer_form,
        'form2': Transcation_form,
        'shopping_list': Cart_list,
        "Cart_nums": len(cart_obj) if isinstance(cart_obj, list) else 0,
    }
    return render(request, 'shopping/order.html', context)


def complete_page(request, order_id):
    mom_plant = MomPlantModel.objects
    transaction = get_object_or_404(TransactionModel, OrderID=order_id)
    order_list = OrderModel.objects.all().filter(OrderID=order_id)
    customer_id = transaction.customer.id
    customers = get_object_or_404(CustomerModel, pk=customer_id)

    # for test
    # check_ok =True

    context = {
        'plant_object': mom_plant,
        'check_ok': check_ok,
        "transaction": transaction,
        "order_list": order_list,
        "customers": customers,
    }

    if check_ok:
        email_template = render_to_string(
            'shopping/email_complete.html',
            context,
            request=request
        )

        email = EmailMultiAlternatives(
            # 信件標題
            '系統完成購買',
            # 信件內容
            email_template,
            # 寄件者
            settings.EMAIL_HOST_USER,
            # 收件者
            [customers.email]
        )
        email.attach_alternative(email_template, "text/html")
        email.fail_silently = False
        # email.send()


    return render(request, 'shopping/complete_page.html', context)


def login_page(request):
    mom_plant = MomPlantModel.objects
    form = LoginModelForm()

    if "login" in request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:

            login(request, user)

            return redirect('/')  # 重新導向到首頁

    context = {
        'plant_object': mom_plant,
        "form": form
    }
    return render(request, 'account/login.html', context)


def register_page(request):

    mom_plant = MomPlantModel.objects
    form = RegisterModelForm()

    if "enroll" in request.POST:
        form = RegisterModelForm(request.POST)
        if form.is_valid():
            # form.save()
            username, password1 = form.cleaned_data["username"], form.cleaned_data["password1"]

            global token_confirm
            token_confirm = Token()

            user = User.objects.create(username=username, password=password1, is_active=False)
            user.set_password(password1)
            user.save()

            token = token_confirm.generate_validate_token(username)

            # https://www.learncodewithmike.com/2020/05/django-send-email.html
            # 電子郵件樣板
            email_template = render_to_string(
                'account/register_check.html',
                {
                    'username': username,
                    'token': token
                },
                request=request
            )

            email = EmailMultiAlternatives(
                # 信件標題
                '系統測試註冊信件',
                # 信件內容
                email_template,
                # 寄件者
                settings.EMAIL_HOST_USER,
                # 收件者
                [username]
            )
            email.attach_alternative(email_template, "text/html")
            email.fail_silently = False
            email.send()

            return redirect('/accounts/login')

    context = {
        'plant_object': mom_plant,
        "form": form
    }
    return render(request, 'account/register.html', context)


def activate_page(request, token):
    """
    the view function is used to accomplish the user register confirm,only after input the link
    that sent to the register email,user can login the site normally.
    :param request:
    :param activate_key:the paragram is gotten by encrypting username when user register
    :return:
    """
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        messages.info(request, '驗證連結已經過期。')
        return HttpResponseRedirect('/accounts/login')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.info(request, '所驗證的使用者不存在，請重新註冊。')
        return HttpResponseRedirect('/accounts/login')

    user.is_active = True
    user.save()
    messages.success(request, '驗證成功，請進行登入操作。')
    return HttpResponseRedirect('/accounts/login')


def logout_page(request):
    logout(request)
    return redirect('/accounts/login')