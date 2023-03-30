import uuid

from django.db import models

from cart_api.protocol import Merchandise

# Create your models here.
class UserModel(models.Model):
    username = models.CharField("使用者帳號", max_length=30, null=False)
    token = models.UUIDField("token", default=uuid.uuid4, editable=False)
    is_auth = models.BooleanField("是否為會員", default=False)
    created_date = models.DateTimeField("創建日期", auto_now_add=True)
    latest_activate_date = models.DateTimeField("最後活躍時間", auto_now=True)

    class Meta:
        unique_together = (
            ("username", "token", ),
            ("username", "is_auth",),
        )


class CartModel(models.Model):
    quantity = models.PositiveSmallIntegerField("數量", default=1, null=False, blank=False)
    valid = models.BooleanField("是否有效", default=True, )
    created_date = models.DateTimeField("創建日期", auto_now_add=True)

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="user_related",
        related_query_name="user_query",
    )

    product = models.ForeignKey(
        "ProductModel",
        on_delete=models.CASCADE,
        related_name="product_related",
        related_query_name="product_query",
    )

class ProductModel(models.Model):

    class Status(models.TextChoices):
        ITINERARY = 'I', "有庫存"
        OUT_OF_STOCK = 'O', "無庫存"

    product_id = models.CharField("產品編碼", max_length=30)
    product_name = models.CharField("產品名稱", max_length=500)
    price = models.PositiveSmallIntegerField("價格", blank=False)
    sale_price = models.PositiveSmallIntegerField("特價價格", blank=True, null=True)
    inventory = models.PositiveSmallIntegerField("庫存", blank=False)

    class_name = models.CharField("類別名稱", max_length=50)
    app_name = models.CharField("APP名稱", max_length=50)

    created_date = models.DateTimeField(auto_now_add=True)
    latest_update_date = models.DateTimeField(auto_now=True)



