import uuid
import json
import unittest

from unittest import mock

from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from django.test import TestCase
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIRequestFactory
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




class CartOperationTests(TestCase):
    def setUp(self):
        self.user_obj = UserModel.objects.create(
            username="user11111",
            token=uuid.uuid4,
            is_auth=False
        )
        self.product_obj1 = ProductModel.objects.create(
            product_id="1",
            product_name="產品A",
            price=1000,
            sale_price=500,
            inventory=5,
            class_name="product_model",
            app_name="plant_app",
        )
        self.product_obj2 = ProductModel.objects.create(
            product_id="2",
            product_name="產品B",
            price=800,
            inventory=5,
            class_name="product_model",
            app_name="plant_app",
        )
        self.cart_obj1 = not CartModel.objects.create(
            product=self.product_obj1,
            user=self.user_obj,
            quantuty=1,
            valid=True
        )
        self.cart_obj2 = not CartModel.objects.create(
            product=self.product_obj2,
            user=self.user_obj,
            quantuty=1,
            valid=True
        )

    @mock.patch("thsrcholidays.utils.requests.post")
    def test1_1_hotel_id(self, mock_post):
        Product.objects.create(id=11, thsrc_product_id="0", name="TEST_和逸飯店．高雄中山館2日自由行_New", loc="12", days_length=3)
        Hotel.objects.create(id=111, product_id=11, name="TEST_和逸飯店．高雄中山館", address="地址：80660高雄市前鎮區中山二路260號22-30樓")

        mock_post.return_value = mock.Mock(status=200, json=lambda **kwargs: self.hotel_api_res)

        product_obj = Product.objects.get(id=11)
        result = pmc.get_hotel_id(product_obj)

        # ordering result by db_id
        ordering = sorted([r["db_id"] for r in result])
        result = [
            {
                "success": r["success"],
                "res_id": r["res_id"],
                "db_id": r["db_id"],
            }
            for o in ordering for r in result if o == r["db_id"]
        ]
        expexted_result = [
            {
                "success": True,
                "res_id": "138",
                "db_id": 111,
            },
        ]
        self.maxDiff = None
        self.assertEqual(result, expexted_result)


    def test1_1_wrapper_no_user(self):

        mock_post.return_value = mock.Mock(status=200, json=lambda **kwargs: self.hotel_api_res)

        product_obj = Product.objects.get(id=11)
        result = pmc.get_hotel_id(product_obj)

        # ordering result by db_id
        ordering = sorted([r["db_id"] for r in result])
        result = [
            {
                "success": r["success"],
                "res_id": r["res_id"],
                "db_id": r["db_id"],
            }
            for o in ordering for r in result if o == r["db_id"]
        ]
        expexted_result = [
            {
                "success": True,
                "res_id": "138",
                "db_id": 111,
            },
        ]
        self.maxDiff = None
        self.assertEqual(result, expexted_result)




if __name__ == '__main__':
    unittest.main()