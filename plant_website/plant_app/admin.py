from django.contrib import admin
from .models import PlantModel, CustomerModel

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "customer", "email", "tel", "address", "qty", "deal_date")

# uesr: admin0 password: bpxu31p4204
# Register your models here.
admin.site.register(PlantModel)
admin.site.register(CustomerModel, CustomerAdmin)