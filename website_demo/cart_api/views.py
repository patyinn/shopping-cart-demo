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
            return JsonResponse(content, status=status_code, safe=False)
        return wrap

    @__process_data
    def get(self, request):
        user = UserModel.objects.get(username="user001")
        cart_obj = CartModel.objects.filter(user=user)
        if not cart_obj:
            return (
                {"message": "No data"},
                status.HTTP_200_OK
            )
        cart_serializer = CartSerializer(cart_obj, many=True)
        print(cart_serializer)
        return (
            cart_serializer.data,
            status.HTTP_200_OK
        )

    @__process_data
    def post(self, request, format=None):
        cart_data = json.loads(json.dumps(request.POST))

        sorted_product = {
            "product_id": cart_data["product_id"],
            "product_name": cart_data["product_name"],
            "price": cart_data["product_price"],
            "inventory": cart_data["product_inventory"],
            "class_name": cart_data["product_class_name"],
            "app_name": cart_data["product_app_name"],
    }

        if cart_data.get("product_sale_price"):
            sorted_product["sale_price"] = cart_data["product_sale_price"]

        cart_data["product"] = sorted_product
        cart_serializer = CartSerializer(data=cart_data)

        if cart_serializer.is_valid():
            cart_serializer.save()

            return (
                cart_serializer.data,
                status.HTTP_201_CREATED
            )
        else:
            return (
                cart_serializer.data,
                status.HTTP_400_BAD_REQUEST
            )


class CartDetail(APIView):
    def __process_data(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
            content, status_code = func(request, *args, **kwargs)
            return JsonResponse(content, status=status_code, safe=False)
        return wrap

    # @__process_data
    # def update(cls, request):
    #     cart_obj = request.session.get(CART_ID)
    #     if not cart_obj:
    #         return (
    #             False,
    #             "No cart object",
    #             "",
    #         )
    #
    #     ids = request.POST.getlist("merchandise_id")
    #     qtys = request.POST.getlist("qty")
    #
    #     session_idxs = {obj["id"]: i for i, obj in enumerate(cart_obj["cart_items"])}
    #     diff_price = 0
    #     for id, qty in zip(ids, qtys):
    #         idx = session_idxs[id]
    #         cart_item = request.session[CART_ID]["cart_items"][idx]
    #         price = cart_item["sale_price"] if cart_item["sale_price"] else cart_item["price"]
    #         new_price = price * int(qty)
    #         diff_price += new_price - cart_item["total_price"]
    #         cart_item.update({
    #             "qty": qty,
    #             "total_price": new_price,
    #         })
    #
    #     request.session[CART_ID]["total_price"] += diff_price
    #     request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
    #     request.session.modified = True
    #
    #     return (
    #         True,
    #         "update cart successfully",
    #         cart_obj,
    #     )
    #
    #
    # @__process_data
    # def remove_cart(cls, request):
    #     cart_obj = request.session.get(CART_ID)
    #     if not cart_obj:
    #         return (
    #             False,
    #             "No cart object",
    #             "",
    #         )
    #
    #     id = request.POST.get("merchandise_id")
    #
    #
    #     session_idxs = [i for i, obj in enumerate(cart_obj["cart_items"]) if obj["id"] == id]
    #     session_idxs.sort(reverse=True)
    #
    #     if session_idxs:
    #         diff_price = 0
    #         for ss_idx in session_idxs:
    #             cart_item = request.session[CART_ID]["cart_items"][ss_idx]
    #             name = cart_item["name"]
    #             diff_price += cart_item["total_price"]
    #             del cart_item
    #
    #         request.session[CART_ID]["total_price"] -= diff_price
    #         request.session[CART_ID]["cart_amount"] = len(request.session[CART_ID]["cart_items"])
    #         request.session.modified = True
    #
    #         return (
    #             True,
    #             "remove {} from cart".format(name),
    #             cart_obj,
    #         )
    #
    #     else:
    #         return (
    #             False,
    #             "this item is not in the cart",
    #             cart_obj,
    #         )