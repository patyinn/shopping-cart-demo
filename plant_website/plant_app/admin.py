from django.contrib import admin
from .models import MomPlantModel, ChildPlantModel, ChildImageModel, CustomerModel

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "customer", "email", "tel", "address", "qty", "deal_date")

class ChildImageInline(admin.TabularInline):
    model = ChildImageModel

class ChildPlantInline(admin.TabularInline):
    model = ChildPlantModel

class MomAdmin(admin.ModelAdmin):
    list_display = ("mom", "mom_image")
    list_filter = ['mom']
    inlines = [ChildPlantInline]


class ChildPlantAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "status", "category", "inventory")
    list_filter = ['status', "category"]
    inlines = [ChildImageInline]

class ChildImageAdmin(admin.ModelAdmin):
    # list_display = ("name", "main_image")
    pass


# uesr: admin0 password: bpxu31p4204
# Register your models here.
admin.site.register(MomPlantModel, MomAdmin)
admin.site.register(ChildPlantModel, ChildPlantAdmin)
admin.site.register(ChildImageModel, ChildImageAdmin)
admin.site.register(CustomerModel, CustomerAdmin)