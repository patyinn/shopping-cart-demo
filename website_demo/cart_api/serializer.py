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

    def create(self, validated_data):
        try:
            ProductModel.objects.get(
                product_id=validated_data["product_id"],
                class_name=validated_data["class_name"],
                app_name=validated_data["app_name"],
            )
            raise serializers.ValidationError("The model has exist")
        except ProductModel.DoesNotExist:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError("error, message is {}".format(e))



class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())

    class Meta:
        model = CartModel
        fields = (
            "id",
            "product",
            "user",
            "quantity",
            "valid",
        )
        read_only_fields = ['id']

    def save(self):
        user_obj = self.validated_data.get("user")
        product_info = self.validated_data.pop("product")

        if not self.instance:
            try:
                product_obj = ProductModel.objects.get(
                    product_id=product_info["product_id"],
                    class_name=product_info["class_name"],
                    app_name=product_info["app_name"],
                )
                self.validated_data["product"] = product_obj

                exist_cart_obj = CartModel.objects.filter(
                    user=user_obj,
                    product=product_obj
                )
                inventory = int(product_obj.inventory)
                if exist_cart_obj:
                    exist_cart_obj = exist_cart_obj[0]
                    self.validated_data["quantity"] += int(exist_cart_obj.quantity)
                    if self.validated_data["quantity"] > product_obj.inventory:
                        self.validated_data["quantity"] = int(product_obj.inventory)
                    self.instance = exist_cart_obj
            except ProductModel.DoesNotExist:
                product_obj = ProductModel(**product_info)
                product_obj.save()

                inventory = product_obj.inventory
                self.validated_data["product"] = product_obj
        else:
            inventory = product_info["inventory"]
            if self.validated_data["quantity"] > int(product_info["inventory"]):
                self.validated_data["quantity"] = int(product_info["inventory"])
            if self.validated_data["quantity"] == 0:
                self.validated_data["valid"] = False

        if inventory == 0:
            self.validated_data["quantity"] = 0
            self.validated_data["valid"] = False

        super().save()

