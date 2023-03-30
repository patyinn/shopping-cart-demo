from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.
def path(instance, filename):
    return 'gallery/{0}/{1}'.format(instance.name, filename)


class AccountManager(BaseUserManager):
    def create_user(self, email, telephone, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
          )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = AccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'telephone']

    def __str__(self):
        return self.email

    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin


class MomPlantModel(models.Model):

    mom = models.CharField(max_length=50, unique=True)
    mom_image = models.ImageField(upload_to='gallery/mom/')

    def __str__(self):
        return str(self.mom) if self.mom else ''


class ChildPlantModel(models.Model):
    class Status(models.TextChoices):
        ITINERARY = 'I', "有庫存"
        OUT_OF_STOCK = 'O', "無庫存"

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=500)
    price = models.PositiveSmallIntegerField(blank=False)
    sale_price = models.PositiveSmallIntegerField(blank=True, null=True)
    inventory = models.PositiveSmallIntegerField(default=1)
    main_image = models.ImageField(upload_to=path)
    category = models.ForeignKey("MomPlantModel", to_field="mom", on_delete=models.CASCADE,
                             blank=False, help_text="須從母株模型資料庫新增")

    status = models.CharField(max_length=1, choices=Status.choices, blank=True, default="I")

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

    customer = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    tel = PhoneNumberField(blank=False, null=False)
    username = models.EmailField(blank=True, null=True)

    def __str__(self):
        return str(self.customer) if self.customer else ''


class TransactionModel(models.Model):

    OrderID = models.CharField(max_length=50, blank=False, unique=True)  # 訂單編號
    customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, blank=False)  # 客戶姓名
    payment_method = [
        ("B", "匯款")
    ]
    payment = models.CharField(max_length=1, choices=payment_method, blank=False, default="B")  # 付款方式
    delivery_method = (
        ("S", "7-11交貨便 -- (估)60元"),
        ("P", "郵局宅配  -- (估)80元"),
        ("F", "面交  -- 限景安/景平捷運站")
    )
    delivery = models.CharField(max_length=1, choices=delivery_method, blank=False, default="S")
    address = models.CharField(max_length=50)  # 運送地址
    comment = models.CharField(max_length=500, null=True, blank=True)
    shipping_fee = models.PositiveSmallIntegerField(null=True, blank=True)  # 運費
    total_payment = models.PositiveIntegerField(blank=False)  # 付款總額
    deal_date = models.DateField(default=timezone.now)  # 成交時間
    show_info = models.BooleanField(default=False)

    def __str__(self):
        return str(self.OrderID) if self.OrderID else ''


class OrderModel(models.Model):
    OrderID = models.ForeignKey(TransactionModel, to_field="OrderID", on_delete=models.CASCADE, blank=False)
    product = models.ForeignKey(ChildPlantModel, to_field="name", on_delete=models.CASCADE, blank=False)
    price = models.PositiveSmallIntegerField(blank=False)
    qty = models.PositiveSmallIntegerField(blank=False, default=1)
    total_price = models.PositiveSmallIntegerField(blank=False)

    def __str__(self):
        return str(self.OrderID) if self.OrderID else ''
