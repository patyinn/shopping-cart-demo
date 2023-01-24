from django.contrib import admin
from .models import MomPlantModel, ChildPlantModel, ChildImageModel, CustomerModel, TransactionModel, OrderModel
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

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
    list_display = ("name", "price", "sale_price", "status", "category", "inventory")
    list_filter = ['status', "category"]
    inlines = [ChildImageInline, OrderInline]

    # test for per-view picture
    # 用 html 語法嵌入 Admin 頁面
    def image_tag(self, obj):
        try:
            img = mark_safe('<img src="%s" width="200px" />' % obj.main_image.url)
        except Exception as e:
            img = ''
        return img
    # 欄位名稱
    image_tag.short_description = _('main_image')
    # 允許執行 image_tag 中回傳的 html 語法，若為 False(預設)則會被視為純文字
    image_tag.allow_tags = True

    # 將 image_tag 函示加入成為其中一個欄位
    readonly_fields = ['image_tag', ]

class ChildImageAdmin(admin.ModelAdmin):
    list_filter = ['name']

    # 用 html 語法嵌入 Admin 頁面
    def image_tag(self, obj):
        try:
            img = mark_safe('<img src="/media/%s" width="200px" />' % obj.imageA)
        except Exception as e:
            img = ''
        return img
    # 欄位名稱
    image_tag.short_description = _('imageA')
    # 允許執行 image_tag 中回傳的 html 語法，若為 False(預設)則會被視為純文字
    image_tag.allow_tags = True

    # 將 image_tag 函示加入成為其中一個欄位
    readonly_fields = ['image_tag', ]


class CustomerAdmin(admin.ModelAdmin):
    list_filter = ['username']
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