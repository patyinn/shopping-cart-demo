import json
from functools import wraps
from pprint import pprint

from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import status

from cart_api.models import UserModel, CartModel, ProductModel
from cart_api.serializer import CartSerializer


def _process_data(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        user_obj = UserModel.objects.get(username="user001")
        content, status_code = func(request, user_obj=user_obj, *args, **kwargs)
        return JsonResponse(content, status=status_code, safe=False)
    return wrap

# Create your views here.
class CartList(APIView):
    @_process_data
    def get(self, request, **kwargs):
        user_obj = kwargs.get("user_obj")
        cart_obj = CartModel.objects.filter(user=user_obj)
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

    @_process_data
    def post(self, request, **kwargs):
        user_obj = kwargs.get("user_obj")

        cart_data = json.loads(json.dumps(request.POST))
        cart_data["user"] = user_obj.pk

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
                cart_serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )


class CartDetail(APIView):
    @_process_data
    def get(self, request, entry_id, **kwargs):
        user_obj = kwargs.get("user_obj")
        try:
            cart_obj = CartModel.objects.get(pk=entry_id, user=user_obj)
            cart_serializer = CartSerializer(cart_obj)
            return (
                cart_serializer.data,
                status.HTTP_200_OK
            )
        except CartModel.DoesNotExist:
            return (
                {"message": "No such entry in cart"},
                status.HTTP_204_NO_CONTENT
            )

    @_process_data
    def put(self, request, entry_id, **kwargs):
        user_obj = kwargs.get("user_obj")

        return (
            cart_serializer.data,
            status.HTTP_200_OK
        )


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