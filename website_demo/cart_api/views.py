import datetime
import json
from functools import wraps
import uuid
from pprint import pprint

from django.http.response import JsonResponse
from django.conf import settings
from django.utils.timezone import make_aware

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from cart_api.models import UserModel, CartModel, ProductModel
from cart_api.serializer import CartSerializer, ProductSerializer


def _process_data(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        request = args[-1] if args else ""
        if not hasattr(request, "user"):
            return JsonResponse(
                {
                    "message": "user not found"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                safe=False
            )
        if request.user.is_authenticated:
            user_obj, created = UserModel.objects.get_or_create(
                username=request.user.username,
                is_auth=True,
                defaults={"token": uuid.uuid4()}
            )
        else:
            username = request.COOKIES.get("cart_username")
            cart_token = request.COOKIES.get(settings.CART_KEY)
            # cart_token = request.session.get(settings.CART_KEY)
            try:
                user_obj = UserModel.objects.get(
                    username=username,
                    token=cart_token,
                    is_auth=False,
                )
            except UserModel.DoesNotExist:
                latest = UserModel.objects.last()
                code = int(latest.pk) + 1 if latest else 1
                user_obj = UserModel.objects.create(
                    username=f"user{code}",
                    token=uuid.uuid4(),
                )

        user_obj.latest_activate_date = make_aware(datetime.datetime.now())
        user_obj.save()
        # request.session[settings.CART_KEY] = user_obj.token
        # request.session.modified = True

        content, status_code = func(user_obj=user_obj, *args, **kwargs)

        response = JsonResponse(content, status=status_code, safe=False)
        if not request.user.is_authenticated:
            response.set_cookie(
                "cart_username",
                user_obj.username,
                expires=datetime.datetime.now() + datetime.timedelta(days=30)
            )
            response.set_cookie(
                settings.CART_KEY,
                str(user_obj.token),
                expires=datetime.datetime.now() + datetime.timedelta(days=30)
            )
        return response
    return wrap

# Create your views here.
class CartList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    @_process_data
    def get(self, request, **kwargs):
        user_obj = kwargs.get("user_obj")
        cart_objs = CartModel.objects.select_related("product").filter(user=user_obj)
        if not cart_objs:
            return (
                {
                    "message": "No data"
                },
                status.HTTP_200_OK
            )
        for cart_obj in cart_objs:
            if cart_obj.product.inventory == 0:
                cart_obj.valid = False
                cart_obj.save()

        cart_serializer = CartSerializer(cart_objs, many=True)
        return (
            cart_serializer.data,
            status.HTTP_200_OK
        )

    @_process_data
    def post(self, request, **kwargs):
        user_obj = kwargs.get("user_obj")

        product_serializer = ProductSerializer(data=request.data)

        if product_serializer.is_valid():
            product_data = product_serializer.data
        else:
            return (
                {
                    "message": product_serializer.errors
                },
                status.HTTP_400_BAD_REQUEST
            )

        cart_data = {
            "user": user_obj.pk,
            "product": product_data,
            "quantity": request.data.get("quantity"),
            "valid": request.data.get("valid")
        }

        cart_serializer = CartSerializer(data=cart_data)
        if cart_serializer.is_valid():
            cart_serializer.save()
            return (
                cart_serializer.data,
                status.HTTP_201_CREATED
            )
        else:
            return (
                {
                    "message": cart_serializer.errors
                },
                status.HTTP_400_BAD_REQUEST
            )

    @_process_data
    def delete(self, request, **kwargs):
        user_obj = kwargs.get("user_obj")
        try:
            entries_id = request.data.get("entries", "").split(",")
            cart_objs = CartModel.objects.filter(pk__in=entries_id, user=user_obj)
            cart_objs.delete()
            return (
                {
                    "message": f"delete entry: {entries_id} successfully"
                },
                status.HTTP_200_OK
            )
        except Exception as e:
            return (
                {
                    "message": f"Error happens because of {e}"
                },
                status.HTTP_400_BAD_REQUEST
            )

class CartDetail(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    @_process_data
    def get(self, request, entry_id, **kwargs):
        user_obj = kwargs.get("user_obj")
        try:
            cart_obj = CartModel.objects.select_related("product").get(pk=entry_id, user=user_obj)
            if cart_obj.product.inventory == 0:
                cart_obj.valid = False
                cart_obj.save()
            cart_serializer = CartSerializer(cart_obj)
            return (
                cart_serializer.data,
                status.HTTP_200_OK
            )
        except CartModel.DoesNotExist:
            return (
                {
                    "message": "No such entry in cart"
                },
                status.HTTP_200_OK
            )
        except Exception as e:
            return (
                {
                    "message": f"Error happens because of {e}"
                },
                status.HTTP_400_BAD_REQUEST
            )

    @_process_data
    def put(self, request, entry_id, **kwargs):
        user_obj = kwargs.get("user_obj")
        try:
            cart_obj = CartModel.objects.get(pk=entry_id, user=user_obj)

            product_serializer = ProductSerializer(data=request.data)

            if product_serializer.is_valid():
                product_data = product_serializer.data
            else:
                return (
                    {
                        "message": product_serializer.errors
                    },
                    status.HTTP_400_BAD_REQUEST
                )

            cart_data = {
                "user": user_obj.pk,
                "product": product_data,
                "quantity": request.data.get("quantity"),
                "valid": request.data.get("valid")
            }
            cart_serializer = CartSerializer(cart_obj, data=cart_data)

            if cart_serializer.is_valid():
                cart_serializer.save()
                return (
                    cart_serializer.data,
                    status.HTTP_200_OK
                )
            else:
                return (
                    {
                        "message": cart_serializer.errors
                    },
                    status.HTTP_400_BAD_REQUEST
                )
        except CartModel.DoesNotExist:
            return (
                {
                    "message": f"The entry: {entry_id} does not exist in cart"
                },
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return (
                {
                    "message": f"Error happens because of {e}"
                },
                status.HTTP_400_BAD_REQUEST
            )

    @_process_data
    def delete(self, request, entry_id, **kwargs):
        user_obj = kwargs.get("user_obj")
        try:
            cart_obj = CartModel.objects.get(pk=entry_id, user=user_obj)
            cart_obj.delete()
            return (
                {
                    "message": f"delete entry: {entry_id} successfully"
                },
                status.HTTP_200_OK
            )
        except CartModel.DoesNotExist:
            return (
                {
                    "message": f"The entry: {entry_id} does not exist in cart"
                },
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return (
                {
                    "message": f"Error happens because of {e}"
                },
                status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET", "POST", "PUT", "DELETE"])
@_process_data
def product_process(request, product_id, class_name, app_name, **kwargs):
    request_data = dict(request.data)
    request_data = {
        k: (v[0] if isinstance(v, list) else v)
        for k, v in request_data.items()
    }
    request_data["product_id"] = product_id
    request_data["class_name"] = class_name
    request_data["app_name"] = app_name

    if not request_data.get("sale_price"):
        request_data["sale_price"] = None

    try:
        product_objs = ProductModel.objects.filter(
            product_id=product_id,
            class_name=class_name,
            app_name=app_name,
        )

        if len(product_objs) > 1:
            return (
                {
                    "message": "duplicate products (id, class and app) in database"
                },
                status.HTTP_200_OK
            )

        elif not product_objs:
            if request.method == "POST":
                product_serializer = ProductSerializer(data=request_data)
                if product_serializer.is_valid():
                    product_serializer.save()
                    return (
                        product_serializer.data,
                        status.HTTP_201_CREATED
                    )
                return (
                    {
                        "message": product_serializer.errors
                    },
                    status.HTTP_400_BAD_REQUEST
                )
            return (
                {
                    "message": "product doesn't register in database"
                },
                status.HTTP_200_OK
            )

        else:
            product_obj = product_objs[0]

        if request.method == "GET":
            product_serializer = ProductSerializer(product_obj)
            return (
                product_serializer.data,
                status.HTTP_200_OK
            )
        elif request.method == "PUT":
            product_serializer = ProductSerializer(product_obj, data=request_data)
            if product_serializer.is_valid():
                product_serializer.save()
                return (
                    product_serializer.data,
                    status.HTTP_200_OK
                )
            return (
                {
                    "message": product_serializer.errors
                },
                status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "POST":
            return (
                {
                    "message": f"The item has existed. entry id is {product_obj.pk}"
                },
                status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "DELETE":
            product_obj.delete()
            return (
                {
                    "message": "The item has deleted."
                },
                status.HTTP_200_OK
            )

    except Exception as e:
        return (
            {
                "message": f"Error happens because of {e}"
            },
            status.HTTP_400_BAD_REQUEST
        )

