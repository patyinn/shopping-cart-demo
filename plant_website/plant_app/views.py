from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from .models import MomPlantModel, ChildPlantModel, ChildImageModel, CustomerModel, TransactionModel, OrderModel
from cart.cart import Cart
from .forms import CustomerModelForm, TranscationModelForm
import datetime
import os
import pandas as pd

# Create your views here.
def index(request):

    plant = MomPlantModel.objects
    num = Cart(request).count()
    context = {
        'plant_object': plant,
        "Cart_nums": num
    }
    return render(request, 'index.html', context)

def category_page(request, mom):
    plant = ChildPlantModel.objects.all().filter(category=mom)
    num = Cart(request).count()
    image = []
    for i in plant:
        image.append(get_object_or_404(ChildImageModel, name=i))
    context = {
        'item': plant,
        # https://bootstrap5.hexschool.com/docs/5.0/components/carousel/#how-it-works
        # https://blog.csdn.net/qq_44302282/article/details/108326844
        # 輪播插件
        'images': image,
        "Cart_nums": num
    }
    return render(request, 'category.html', context)

def plant_page(request, child):

    plant_detail = get_object_or_404(ChildPlantModel, name=child)
    plant_image = ChildImageModel.objects.get(name=child)
    mom = plant_detail.category
    plant = ChildPlantModel.objects.all().filter(category=mom)
    image_list = [i for i in vars(plant_image).values()][3:]
    image_list = [os.path.join('/media', str(i)) for i in image_list if i != '']
    image_list.insert(0, plant_detail.main_image.url)
    num = Cart(request).count()

    context = {
        'item': plant,
        'details': plant_detail,
        'images': image_list,
        "Cart_nums": num
    }
    return render(request, 'plants/detail.html', context)

# https://cloud.tencent.com/developer/article/1174798
def add_to_cart(request, product):
    product = ChildPlantModel.objects.get(name=product)
    cart = Cart(request)
    quantity = 1
    cart.add(product, product.price, quantity)
    return redirect('/Entry/{}'.format(product))

def remove_from_cart(request, product):
    product = ChildPlantModel.objects.get(name=product)
    Cart_list = Cart(request)
    Cart_list.remove(product)
    return redirect('/Cart')


def Update_cart(request, product):
    if 'update' in request.POST:
        qty = request.POST["qty"]
        product = ChildPlantModel.objects.get(name=product)
        Cart_list = Cart(request)
        Cart_list.update(product, qty, product.price)
        return redirect('/Cart')
    else:
        pass

# https://stackoverflow.com/questions/64915167/how-do-i-use-a-django-url-inside-of-an-option-tag-in-a-dropdown-menu
def get_cart(request):
    plant_detail = ChildPlantModel.objects
    Cart_list = Cart(request)
    num = Cart_list.count()
    inv_list = []
    image_list = []
    for item in Cart_list:
        plant = item.product.name
        model = plant_detail.get(name=plant)
        price = model.price
        qty = int(item.quantity)
        inv = int(model.inventory)
        if qty >= inv:
            Cart_list.update(model, inv, price)
        inv_list.append([i + 1 for i in range(inv)])
        image_list.append(model.main_image)

    context = {
        'cart': Cart_list,
        'inv_list': inv_list,
        'image_list': image_list,
        'product': plant_detail,
        "Cart_nums": num
    }
    return render(request, 'cart.html', context)

def order_page(request):

    plant_inventory = ChildPlantModel.objects
    Customer_form = CustomerModelForm()
    Transcation_form = TranscationModelForm()
    Cart_list = Cart(request)
    num = Cart_list.count()

    # 取得從購物車中確認的購買資料
    Cart_data = pd.DataFrame()
    for item in Cart_list:
        Cart_data = Cart_data.append({
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'total_price': item.total_price,
        }, ignore_index=True)
    Cart_data = Cart_data.set_index(['name'])

    if 'purchase' in request.POST:
        form1 = CustomerModelForm(request.POST)
        form2 = CustomerModelForm(request.POST)
        global check_ok
        # 逐一檢查商品狀態與數量是否符合存貨
        for prod in Cart_data.index:
            inv = plant_inventory.get(name=prod).inventory
            status = plant_inventory.get(name=prod).status
            qty = int(Cart_data.loc[prod, "quantity"])

            if inv >= qty and status == "I":
                check_ok = True
            else:
                check_ok = False
                product = plant_inventory.get(name=prod)
                Cart_list.remove(product)
                break

        if check_ok:
            if form1.is_valid() and form2.is_valid():

                # 新增客戶資料至客戶系統模型上
                customer = request.POST["customer"]
                email = request.POST["email"]
                tel = request.POST["tel"]
                if CustomerModel.objects.filter(customer=customer).exists():
                    CustomerModel.objects.filter(customer=customer).update(
                        customer=customer,
                        tel=tel,
                        email=email,
                    )
                else:
                    # 新增客戶資料至客戶系統模型上
                    CustomerModel.objects.create(
                        customer=customer,
                        tel=tel,
                        email=email,
                    )

                # 新增訂單資訊至交易系統模型上
                deal_date = datetime.datetime.now()
                OrderID = datetime.datetime.strftime(deal_date, "%Y%m%d%H%M%S")
                # customer_fk = CustomerModel.objects.only('customer').get(customer=customer)
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
                )

                # 新增訂單詳細內容至訂單系統模型上
                for prod in Cart_data.index:
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

                Cart_list.clear()
                return redirect('/OrderComplete/{}'.format(OrderID))


    context = {
        'form1': Customer_form,
        'form2': Transcation_form,
        'shopping_list': Cart_list,
        "Cart_nums": num
    }
    return render(request, 'order.html', context)


def complete_page(request, id):
    transaction = get_object_or_404(TransactionModel, OrderID=id)
    order_list = OrderModel.objects.all().filter(OrderID=id)
    name = transaction.customer
    customers = get_object_or_404(CustomerModel, customer=name)

    context = {
        'check_ok': check_ok,
        "transaction": transaction,
        "order_list": order_list,
        "customers": customers
    }
    return render(request, 'plants/complete_page.html', context)