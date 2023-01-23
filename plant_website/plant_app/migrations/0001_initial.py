# Generated by Django 4.1 on 2022-12-31 09:00

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import plant_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChildPlantModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, unique=True)),
                ('description', models.CharField(max_length=500)),
                ('price', models.PositiveSmallIntegerField()),
                ('sale_price', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('inventory', models.PositiveSmallIntegerField(default=1)),
                ('main_image', models.ImageField(upload_to=plant_app.models.path)),
                ('status', models.CharField(blank=True, choices=[('I', '有庫存'), ('O', '無庫存')], default='I', max_length=1)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CustomerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('tel', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('username', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MomPlantModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mom', models.CharField(max_length=50, unique=True)),
                ('mom_image', models.ImageField(upload_to='gallery/mom/')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OrderID', models.CharField(max_length=50, unique=True)),
                ('payment', models.CharField(choices=[('B', '匯款')], default='B', max_length=1)),
                ('delivery', models.CharField(choices=[('S', '7-11交貨便 -- (估)60元'), ('P', '郵局宅配  -- (估)80元'), ('F', '面交  -- 限景安/景平捷運站')], default='S', max_length=1)),
                ('address', models.CharField(max_length=50)),
                ('comment', models.CharField(blank=True, max_length=500, null=True)),
                ('shipping_fee', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('total_payment', models.PositiveIntegerField()),
                ('deal_date', models.DateField(default=django.utils.timezone.now)),
                ('show_info', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plant_app.customermodel')),
            ],
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveSmallIntegerField()),
                ('qty', models.PositiveSmallIntegerField(default=1)),
                ('total_price', models.PositiveSmallIntegerField()),
                ('OrderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plant_app.transactionmodel', to_field='OrderID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plant_app.childplantmodel', to_field='name')),
            ],
        ),
        migrations.AddField(
            model_name='childplantmodel',
            name='category',
            field=models.ForeignKey(help_text='須從母株模型資料庫新增', on_delete=django.db.models.deletion.CASCADE, to='plant_app.momplantmodel', to_field='mom'),
        ),
        migrations.CreateModel(
            name='ChildImageModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageA', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('imageB', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('imageC', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('imageD', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('imageE', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('imageF', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('imageG', models.ImageField(blank=True, null=True, upload_to=plant_app.models.path)),
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='plant_app.childplantmodel', to_field='name')),
            ],
        ),
    ]
