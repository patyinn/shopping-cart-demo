from rest_framework import serializers
from cart_api.models import CartModel, UserModel, ProductModel


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = (
            "id",
            "product_id",
            "product_name",
            "price",
            "sale_price",
            "inventory",
            "class_name",
            "app_name",
        )


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())

    class Meta:
        model = CartModel
        fields = (
            "product",
            "user",
            "quantity",
            "valid",
        )

    def save(self):
        user_obj = self.validated_data.get("user")
        print(user_obj)
        print(user_obj.id)
        product_info = self.validated_data.pop("product")

        try:
            product_obj = ProductModel.objects.get(
                product_id=product_info["product_id"],
                class_name=product_info["class_name"],
                app_name=product_info["app_name"],
            )
            product_obj.price = product_info["price"]
            if product_info.get("sale_price"):
                product_obj.sale_price = product_info["sale_price"]
            product_obj.inventory = product_info["inventory"]
            product_obj.save()
            self.validated_data["product"] = product_obj

            exist_cart_obj = CartModel.objects.filter(
                user=user_obj,
                product=product_obj
            )
            if exist_cart_obj:
                exist_cart_obj = exist_cart_obj[0]
                self.validated_data["quantity"] += int(exist_cart_obj.quantity)
                if self.validated_data["quantity"] > product_obj.inventory:
                    self.validated_data["quantity"] = int(product_obj.inventory)
                self.instance = exist_cart_obj

        except ProductModel.DoesNotExist:
            product_obj = ProductModel(**product_info)
            product_obj.save()

            self.validated_data["product"] = product_obj

        super().save()

