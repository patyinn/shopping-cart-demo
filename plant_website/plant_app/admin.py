from django.contrib import admin
from .models import MomPlantModel, ChildPlantModel, ChildImageModel, CustomerModel, TransactionModel, OrderModel

class ChildImageInline(admin.TabularInline):
    model = ChildImageModel

class ChildPlantInline(admin.TabularInline):
    model = ChildPlantModel

class OrderInline(admin.TabularInline):
    model = OrderModel

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class TransactionInline(admin.TabularInline):
    model = TransactionModel

    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class MomAdmin(admin.ModelAdmin):
    list_display = ("mom", "mom_image")
    list_filter = ['mom']
    inlines = [ChildPlantInline]

class ChildPlantAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "status", "category", "inventory")
    list_filter = ['status', "category"]
    inlines = [ChildImageInline, OrderInline]

class ChildImageAdmin(admin.ModelAdmin):
    list_filter = ['name']

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer", "email", "tel")
    inlines = [TransactionInline]

    def has_change_permission(self, request, obj=None):
        return False

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("OrderID", "customer", "delivery", "total_payment", "deal_date")
    list_filter = ["customer", "delivery"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    inlines = [OrderInline]

class OrderAdmin(admin.ModelAdmin):
    list_display = ("OrderID", "product", "price", "qty")

    readonly_fields = ["OrderID", "product", "price", "qty"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# uesr: admin0 password: bpxu31p4204
# Register your models here.
admin.site.register(MomPlantModel, MomAdmin)
admin.site.register(ChildPlantModel, ChildPlantAdmin)
admin.site.register(ChildImageModel, ChildImageAdmin)
admin.site.register(CustomerModel, CustomerAdmin)
admin.site.register(TransactionModel, TransactionAdmin)
admin.site.register(OrderModel, OrderAdmin)