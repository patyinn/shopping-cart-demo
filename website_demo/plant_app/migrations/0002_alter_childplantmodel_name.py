# Generated by Django 4.1 on 2023-02-21 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='childplantmodel',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
