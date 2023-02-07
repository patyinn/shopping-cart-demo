from rest_framework import serializers
from cart_api.models import CartModel, UserModel, ProductModel

class CartSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=ProductModel.objects.using("cart").all(), many=False)
    product_id = serializers.CharField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_price = serializers.CharField(source="product.price", read_only=True)
    product_sale_price = serializers.CharField(source="product.sale_price", read_only=True)
    product_inventory = serializers.CharField(source="product.inventory", read_only=True)
    product_class_name = serializers.CharField(source="product.class_name", read_only=True)
    product_app_name = serializers.CharField(source="product.app_name", read_only=True)
    user_username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = CartModel
        fields = (
            "product",
            "product_id",
            "product_name",
            "product_price",
            "product_sale_price",
            "product_inventory",
            "product_class_name",
            "product_app_name",
            "user_username",
            "quantity",
            "valid",
        )

    def save_product(self):
        pass


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = (
            "product_id",
            "product_name",
            "price",
            "sale_price",
            "inventory",
            "class_name",
            "app_name",
        )