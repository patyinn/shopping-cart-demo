import json
from functools import wraps
from pprint import pprint

from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import status

from cart_api.models import UserModel, CartModel, ProductModel
from cart_api.serializer import CartSerializer


# Create your views here.
class CartList(APIView):

    def __process_data(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
            content, status_code = func(request, *args, **kwargs)
            return JsonResponse(content, status=status_code)
        return wrap

    @__process_data
    def get(self, request):
        User = request.session.get("user")
        cart_obj = CartModel.objects.filter(user=User).using("cart")
        if not cart_obj:
            return (
                {"message": "No data"},
                status.HTTP_200_OK
            )
        cart_serializer = CartSerializer(cart_obj, many=True)
        return (
            cart_serializer.data,
            status.HTTP_200_OK
        )


    @__process_data
    def post(self, request, format=None):
        cart_data = json.loads(json.dumps(request.POST))
        user = UserModel.objects.using("cart").get(username=request.POST["user"])
        pprint(user.token)

        cart_data["user_username"] = user.username
        cart_data["user_token"] = user.token

        try:
            product_obj = ProductModel.objects.using("cart").get(
                product_id=cart_data["product_id"],
                class_name=cart_data["product_class_name"],
                app_name=cart_data["product_app_name"],
            )
        except ProductModel.DoesNotExist:
            product_value = {
                "product_id": cart_data["product_id"],
                "product_name": cart_data["product_name"],
                "price": cart_data["product_price"],
                "sale_price": cart_data["product_sale_price"],
                "inventory": cart_data["product_inventory"],
                "class_name": cart_data["product_class_name"],
                "app_name": cart_data["product_app_name"],
            }
            product_obj = ProductModel(**product_value)
            product_obj.save()

        cart_data["product"] = str(product_obj.id)

        cart_obj = CartModel.objects.using("cart").filter(user=user)
        cart_item_list = [obj for obj in cart_obj]
        cart_serializer = CartSerializer(cart_obj, data=cart_data)
        print(cart_serializer)
        print(cart_serializer.is_valid())
        print(cart_serializer.errors)
        if cart_serializer.is_valid():
            cart_serializer.save()
            #
            # cart_value = cart_values[0]
            # qty = qty if cart_value["inventory"] >= qty else cart_value["inventory"]
            # cart_value["qty"] = qty
            # price = cart_value["sale_price"] if cart_value["sale_price"] else cart_value["price"]
            # cart_value["total_price"] = int(cart_value["qty"]) * price
            #
            # if not cart_obj:
            #     request.session[CART_ID] = {
            #         "cart_items": [cart_value],
            #         "cart_price": cart_value["total_price"],
            #         "cart_amount": 1,
            #     }
            # else:
            #     request.session[CART_ID]["cart_items"].append(cart_value)
            #     request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
            #     request.session[CART_ID]["total_price"] += cart_value["total_price"]
            #
            # request.session.modified = True

            return (
                cart_serializer.data,
                status.HTTP_201_CREATED
            )
        else:
            return (
                cart_serializer.data,
                status.HTTP_400_BAD_REQUEST
            )



    @__process_data
    def update(cls, request):
        cart_obj = request.session.get(CART_ID)
        if not cart_obj:
            return (
                False,
                "No cart object",
                "",
            )

        ids = request.POST.getlist("merchandise_id")
        qtys = request.POST.getlist("qty")

        session_idxs = {obj["id"]: i for i, obj in enumerate(cart_obj["cart_items"])}
        diff_price = 0
        for id, qty in zip(ids, qtys):
            idx = session_idxs[id]
            cart_item = request.session[CART_ID]["cart_items"][idx]
            price = cart_item["sale_price"] if cart_item["sale_price"] else cart_item["price"]
            new_price = price * int(qty)
            diff_price += new_price - cart_item["total_price"]
            cart_item.update({
                "qty": qty,
                "total_price": new_price,
            })

        request.session[CART_ID]["total_price"] += diff_price
        request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
        request.session.modified = True

        return (
            True,
            "update cart successfully",
            cart_obj,
        )




    @__process_data
    def remove_cart(cls, request):
        cart_obj = request.session.get(CART_ID)
        if not cart_obj:
            return (
                False,
                "No cart object",
                "",
            )

        id = request.POST.get("merchandise_id")


        session_idxs = [i for i, obj in enumerate(cart_obj["cart_items"]) if obj["id"] == id]
        session_idxs.sort(reverse=True)

        if session_idxs:
            diff_price = 0
            for ss_idx in session_idxs:
                cart_item = request.session[CART_ID]["cart_items"][ss_idx]
                name = cart_item["name"]
                diff_price += cart_item["total_price"]
                del cart_item

            request.session[CART_ID]["total_price"] -= diff_price
            request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
            request.session.modified = True

            return (
                True,
                "remove {} from cart".format(name),
                cart_obj,
            )

        else:
            return (
                False,
                "this item is not in the cart",
                cart_obj,
            )