from django.db import models
from django.utils import timezone

# Create your models here.
class PlantModel(models.Model):

    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=225)
    context = models.CharField(max_length=500)
    price = models.IntegerField()
    inventory = models.IntegerField()

    def __str__(self):
        return str(self.title) if self.title else ''


class CustomerModel(models.Model):

    title = models.ForeignKey(PlantModel, on_delete=models.CASCADE, blank=False)
    price = models.IntegerField()
    customer = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    tel = models.IntegerField()
    address = models.CharField(max_length=50)
    qty = models.IntegerField()
    deal_date = models.DateField(default=timezone.now)  # 成交時間

    def __str__(self):
        return str(self.title) if self.title else ''