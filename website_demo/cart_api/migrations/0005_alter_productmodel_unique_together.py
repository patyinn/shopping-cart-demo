# Generated by Django 4.1 on 2023-02-16 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart_api', '0004_usermodel_is_auth_alter_productmodel_product_id_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productmodel',
            unique_together=set(),
        ),
    ]