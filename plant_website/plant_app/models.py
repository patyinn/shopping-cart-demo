from django.db import models
from django.utils import timezone

# Create your models here.
class MomPlantModel(models.Model):

    mom = models.CharField(max_length=50, unique=True)
    mom_image = models.ImageField(upload_to='gallery/mom/')

    def __str__(self):
        return str(self.mom) if self.mom else ''


def path(instance, filename):
    return 'gallery/{0}/{1}'.format(instance.name, filename)

class ChildPlantModel(models.Model):

    name = models.CharField(max_length=500, unique=True)
    description = models.CharField(max_length=500)
    price = models.IntegerField()
    inventory = models.IntegerField(default=1)
    main_image = models.ImageField(upload_to=path)
    category = models.ForeignKey("MomPlantModel", to_field="mom", on_delete=models.CASCADE,
                             blank=False, help_text="須從母株模型資料庫新增")
    PRODUCT_STATUS = (
        ('I', "有庫存"),
        ('O', "無庫存")
    )
    status = models.CharField(max_length=1, choices=PRODUCT_STATUS, blank=True, default="I")
    class Meta:
        ordering = ['name']
    def __str__(self):
        return str(self.name) if self.name else ''

class ChildImageModel(models.Model):
    name = models.OneToOneField("ChildPlantModel", to_field="name", on_delete=models.CASCADE, blank=False)
    imageA = models.ImageField(upload_to=path, null=True, blank=True)
    imageB = models.ImageField(upload_to=path, null=True, blank=True)
    imageC = models.ImageField(upload_to=path, null=True, blank=True)
    imageD = models.ImageField(upload_to=path, null=True, blank=True)
    imageE = models.ImageField(upload_to=path, null=True, blank=True)
    imageF = models.ImageField(upload_to=path, null=True, blank=True)
    imageG = models.ImageField(upload_to=path, null=True, blank=True)

    def __str__(self):
        return str(self.name) if self.name else ''


class CustomerModel(models.Model):

    title = models.ForeignKey(ChildImageModel, on_delete=models.CASCADE, blank=False)
    price = models.IntegerField()
    customer = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    tel = models.IntegerField()
    address = models.CharField(max_length=50)
    qty = models.IntegerField()
    deal_date = models.DateField(default=timezone.now)  # 成交時間

    def __str__(self):
        return str(self.title) if self.title else ''