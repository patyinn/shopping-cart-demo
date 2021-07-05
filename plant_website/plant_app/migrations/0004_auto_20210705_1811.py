# Generated by Django 3.2.4 on 2021-07-05 10:11

from django.db import migrations, models
import plant_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_app', '0003_alter_childplantmodel_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='childimagemodel',
            name='main_image',
        ),
        migrations.AddField(
            model_name='childplantmodel',
            name='main_image',
            field=models.ImageField(default='NO', upload_to=plant_app.models.path),
            preserve_default=False,
        ),
    ]
