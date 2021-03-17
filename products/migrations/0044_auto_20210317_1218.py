# Generated by Django 3.1.7 on 2021-03-17 03:18

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0043_auto_20210316_0233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        migrations.AddField(
            model_name='product',
            name='image1',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image2',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image3',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image4',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image5',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image6',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image7',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image8',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='image9',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
        migrations.AddField(
            model_name='product',
            name='main_image',
            field=models.FileField(blank=True, null=True, upload_to=products.models.upload_main_image_path),
        ),
    ]
