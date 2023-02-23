import uuid
import json
import unittest

from unittest import mock

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.decorators import api_view
from rest_framework.test import force_authenticate

from cart_api.models import UserModel, CartModel, ProductModel
from cart_api.views import (
    _process_data,
    CartList,
    CartDetail
)


# Create your tests here.
class WrapperTests(TestCase):
    databases = "__all__"

    def setUp(self) -> None:
        @api_view(["GET"])
        @_process_data
        def mock_func(*args, **kwargs):
            return (
                {},
                status.HTTP_200_OK
            )

        self.decorated_func = mock_func
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob',
            email='jacob@…',
            password='top_secret'
        )

    def test_1_no_user(self):
        request = self.factory.get('/')
        response = self.decorated_func(request, "test")

        self.assertEqual(
            json.loads(response.content),
            {
                "message": "user not found"
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def test_2_create_user_without_exist_user_db(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        response = self.decorated_func(request)
        username_cookies = response.cookies["cart_username"].__dict__
        token_cookies = response.cookies[settings.CART_KEY].__dict__

        latest = UserModel.objects.last()
        self.assertEqual(latest.username, f"user{latest.pk}")
        self.assertEqual(username_cookies["_value"], UserModel.objects.last().username)
        self.assertEqual(token_cookies["_value"], str(UserModel.objects.last().token))

    def test_3_create_user_with_exist_user_db(self):
        UserModel.objects.create(
            username="user11111",
            token=uuid.uuid4(),
            is_auth=False
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()

        response = self.decorated_func(request)
        username_cookies = response.cookies["cart_username"].__dict__
        token_cookies = response.cookies[settings.CART_KEY].__dict__

        latest = UserModel.objects.last()
        self.assertEqual(latest.username, f"user{latest.pk}")
        self.assertEqual(username_cookies["_value"], UserModel.objects.last().username)
        self.assertEqual(token_cookies["_value"], str(UserModel.objects.last().token))

    def test_4_get_existed_user(self):
        token = uuid.uuid4()
        UserModel.objects.create(
            username="user11111",
            token=token,
            is_auth=False
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.COOKIES["cart_username"] = "user11111"
        request.COOKIES[settings.CART_KEY] = str(token)

        response = self.decorated_func(request)
        username_cookies = response.cookies["cart_username"].__dict__
        token_cookies = response.cookies[settings.CART_KEY].__dict__

        self.assertEqual(username_cookies["_value"], "user11111")
        self.assertEqual(token_cookies["_value"], str(token))

    def test_5_get_existed_user_bur_wrong_token(self):
        token = uuid.uuid4()
        UserModel.objects.create(
            username="user11111",
            token=token,
            is_auth=False
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.COOKIES["cart_username"] = "user11112"
        request.COOKIES[settings.CART_KEY] = str(token)

        response = self.decorated_func(request)
        username_cookies = response.cookies["cart_username"].__dict__
        token_cookies = response.cookies[settings.CART_KEY].__dict__

        latest = UserModel.objects.last()
        self.assertEqual(latest.username, f"user{latest.pk}")
        self.assertEqual(username_cookies["_value"], UserModel.objects.last().username)
        self.assertEqual(token_cookies["_value"], str(UserModel.objects.last().token))

    def test_6_get_existed_user_bur_wrong_username(self):
        token = uuid.uuid4()
        UserModel.objects.create(
            username="user11111",
            token=token,
            is_auth=False
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.COOKIES["cart_username"] = "user11111"
        request.COOKIES[settings.CART_KEY] = str(uuid.uuid4())

        response = self.decorated_func(request)
        username_cookies = response.cookies["cart_username"].__dict__
        token_cookies = response.cookies[settings.CART_KEY].__dict__

        latest = UserModel.objects.last()
        self.assertEqual(latest.username, f"user{latest.pk}")
        self.assertEqual(username_cookies["_value"], UserModel.objects.last().username)
        self.assertEqual(token_cookies["_value"], str(UserModel.objects.last().token))

    def test_7_create_user_is_authenticated(self):
        request = self.factory.get('/')
        force_authenticate(request, user=self.user)

        response = self.decorated_func(request)
        self.assertEqual(UserModel.objects.last().username, "jacob")
        self.assertEqual(len(response.cookies), 0)

    def test_8_get_user_is_authenticated(self):
        token = uuid.uuid4()
        UserModel.objects.create(
            username=self.user.username,
            token=token,
            is_auth=True
        )

        request = self.factory.get('/')
        force_authenticate(request, user=self.user)
        response = self.decorated_func(request)

        self.assertEqual(UserModel.objects.last().username, "jacob")
        self.assertEqual(UserModel.objects.last().token, token)
        self.assertEqual(UserModel.objects.last().is_auth, True)
        self.assertEqual(len(response.cookies), 0)


class CartListTests(TestCase):
    databases = "__all__"

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob',
            email='jacob@…',
            password='top_secret'
        )

        self.user1_token = uuid.uuid4()
        self.user1 = UserModel.objects.create(
            username=self.user.username,
            token=self.user1_token,
            is_auth=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.anonymous_client = APIClient()

        self.product_obj1 = ProductModel.objects.create(
            product_id="1",
            product_name="產品A",
            price=1000,
            sale_price=500,
            inventory=0,
            class_name="plant_model",
            app_name="plant_app",
        )
        self.product_obj2 = ProductModel.objects.create(
            product_id="2",
            product_name="產品B",
            price=800,
            inventory=7,
            class_name="plant_model",
            app_name="plant_app",
        )
        self.cart_obj1 = CartModel.objects.create(
            product=self.product_obj1,
            user=self.user1,
            quantity=1,
            valid=True
        )
        self.cart_obj2 = CartModel.objects.create(
            product=self.product_obj2,
            user=self.user1,
            quantity=2,
            valid=True
        )

    def test_get_existed_data(self):

        response = self.client.get("/api/cart/")

        expected_result = [
            {
                "id": 1,
                "product": {
                    "id": 1,
                    "product_id": "1",
                    "product_name": "產品A",
                    "price": 1000,
                    "sale_price": 500,
                    "inventory": 0,
                    "class_name": "plant_model",
                    "app_name": "plant_app",
                },
                "user": 1,
                "quantity": 1,
                "valid": False,
            },
            {
                "id": 2,
                "product": {
                    "id": 2,
                    "product_id": "2",
                    "product_name": "產品B",
                    "price": 800,
                    'sale_price': None,
                    "inventory": 7,
                    "class_name": "plant_model",
                    "app_name": "plant_app",
                },
                "user": 1,
                "quantity": 2,
                "valid": True,
            },
        ]
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_empty_data(self):

        response = self.anonymous_client.get("/api/cart/")

        expected_result = {
            "message": "No data"
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_new_product(self):
        request_input = {
            "product_id": "3",
            "product_name": "產品C",
            "price": 9000,
            "sale_price": 5000,
            "inventory": 1,
            "class_name": "B_model",
            "app_name": "B_app",
            "quantity": 1,
            "valid": True,
        }
        response = self.client.post("/api/cart/", request_input, json=request_input, format="json")

        expected_result = {
            "id": 3,
            "product": {
                "id": 3,
                "product_id": "3",
                "product_name": "產品C",
                "price": 9000,
                "sale_price": 5000,
                "inventory": 1,
                "class_name": "B_model",
                "app_name": "B_app",
            },
            "user": 1,
            "quantity": 1,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductModel.objects.last().product_id, "3")

    def test_post_product_exist(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 1000,
            "inventory": 7,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 1,
            "valid": True,
        }
        response = self.client.post("/api/cart/", request_input, json=request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                'sale_price': None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 3,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ProductModel.objects.filter(product_id="2")), 1)

    def test_post_product_exist(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 1000,
            "inventory": 7,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 1,
            "valid": True,
        }
        response = self.client.post("/api/cart/", request_input, json=request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                'sale_price': None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 3,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ProductModel.objects.filter(product_id="2")), 1)

    def test_post_product_quantity_max(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 1000,
            "inventory": 7,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 10,
            "valid": True,
        }
        response = self.client.post("/api/cart/", request_input, json=request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                'sale_price': None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 7,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ProductModel.objects.filter(product_id="2")), 1)

    def test_post_cart_lack_content(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品G",
            "price": 5000,
            "sale_price": 800,
            "inventory": 4,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "valid": True,
        }
        response = self.client.post("/api/cart/", request_input, json=request_input, format="json")

        expected_result = {
            'quantity': ['This field may not be null.']
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_product_lack_content(self):
        request_input = {
            "valid": True,
        }
        response = self.client.post("/api/cart/", request_input, json=request_input, format="json")

        expected_result = {
            "product_id": ["這個欄位是必須的。"],
            "product_name": ["這個欄位是必須的。"],
            "price": ["這個欄位是必須的。"],
            "inventory": ["這個欄位是必須的。"],
            "class_name": ["這個欄位是必須的。"],
            "app_name": ["這個欄位是必須的。"],
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartDetailTests(TestCase):
    databases = "__all__"

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob',
            email='jacob@…',
            password='top_secret'
        )

        self.user1_token = uuid.uuid4()
        self.user1 = UserModel.objects.create(
            username=self.user.username,
            token=self.user1_token,
            is_auth=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.anonymous_client = APIClient()

        self.product_obj1 = ProductModel.objects.create(
            product_id="1",
            product_name="產品A",
            price=1000,
            sale_price=500,
            inventory=0,
            class_name="plant_model",
            app_name="plant_app",
        )
        self.product_obj2 = ProductModel.objects.create(
            product_id="2",
            product_name="產品B",
            price=800,
            inventory=7,
            class_name="plant_model",
            app_name="plant_app",
        )
        self.cart_obj1 = CartModel.objects.create(
            product=self.product_obj1,
            user=self.user1,
            quantity=1,
            valid=True
        )
        self.cart_obj2 = CartModel.objects.create(
            product=self.product_obj2,
            user=self.user1,
            quantity=2,
            valid=True
        )

    def test_get_existed_data(self):
        response = self.client.get("/api/cart/1")
        expected_result = {
            "id": 1,
            "product": {
                "id": 1,
                "product_id": "1",
                "product_name": "產品A",
                "price": 1000,
                "sale_price": 500,
                "inventory": 0,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 1,
            "valid": False,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_exist_data(self):
        response = self.client.get("/api/cart/3")
        expected_result = {
            "message": "No such entry in cart"
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_existed_product(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 800,
            "inventory": 7,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 3,
            "valid": True,
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                "sale_price": None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 3,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_existed_product_diff(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 8655,
            "inventory": 4,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 4,
            "valid": True,
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                "sale_price": None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 4,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_existed_product_max(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 800,
            "inventory": 7,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 11,
            "valid": True,
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                "sale_price": None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 7,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_existed_product_zero(self):
        request_input = {
            "product_id": "2",
            "product_name": "產品B",
            "price": 800,
            "inventory": 7,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 0,
            "valid": True,
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                "sale_price": None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 0,
            "valid": False,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_not_exist_product(self):
        request_input = {
            "product_id": "8",
            "product_name": "產品E",
            "price": 400,
            "inventory": 10,
            "class_name": "plant_model",
            "app_name": "plant_app",
            "quantity": 4,
            "valid": True,
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "id": 2,
            "product": {
                "id": 2,
                "product_id": "2",
                "product_name": "產品B",
                "price": 800,
                "sale_price": None,
                "inventory": 7,
                "class_name": "plant_model",
                "app_name": "plant_app",
            },
            "user": 1,
            "quantity": 4,
            "valid": True,
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_product_missing_data(self):
        request_input = {
            "quantity": 1,
            "valid": True,
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "product_id": ["這個欄位是必須的。"],
            "product_name": ["這個欄位是必須的。"],
            "price": ["這個欄位是必須的。"],
            "inventory": ["這個欄位是必須的。"],
            "class_name": ["這個欄位是必須的。"],
            "app_name": ["這個欄位是必須的。"],
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_cart_missing_data(self):
        request_input = {
            "product_id": "8",
            "product_name": "產品E",
            "price": 400,
            "inventory": 10,
            "class_name": "plant_model",
            "app_name": "plant_app",
        }
        response = self.client.put("/api/cart/2", request_input, format="json")

        expected_result = {
            "quantity": ['This field may not be null.'],
            "valid": ['This field may not be null.'],
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existed_data(self):
        response = self.client.delete("/api/cart/1")
        expected_result = {
            "message": f"delete entry: 1 successfully"
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(CartModel.objects.filter(pk=1)), 0)

    def test_delete_not_exist_data(self):
        response = self.client.delete("/api/cart/3")

        expected_result = {
            "message": f"The entry: 3 does not exist in cart"
        }
        self.assertEqual(json.loads(response.content), expected_result)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




if __name__ == '__main__':
    unittest.main()