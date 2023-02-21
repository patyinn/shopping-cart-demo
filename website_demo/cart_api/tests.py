import uuid
import json
import unittest

from unittest import mock

from django.test.client import RequestFactory
from django.test import TestCase
from rest_framework import status

from cart_api.models import UserModel, CartModel, ProductModel
from cart_api.views import (
    _process_data,
    CartList,
    CartDetail
)


# Create your tests here.
class WrapperTests(TestCase):
    def setUp(self) -> None:
        @_process_data
        def mock_func(*args, **kwargs):
            return (
                {},
                status.HTTP_200_OK
            )

        self.decorated_func = mock_func

    def test_1_no_user(self):
        self.assertEqual(
            json.loads(self.decorated_func().content),
            {
                "message": "user not found"
            },
        )
        self.assertEqual(
            self.decorated_func().status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def test_2_create_user_without_exist_user(self):
        request = RequestFactory()
        self.decorated_func(request)

        self.assertEqual(UserModel.objects.last().username, "user1")

    def test_4_get_existed_user(self):
        class MockUser:
            is_active = True
            is_staff = True

            def has_perm(self, *args):
                return True




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