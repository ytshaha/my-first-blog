# Generated by Django 3.1.7 on 2021-02-23 20:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_product_product_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_type',
        ),
    ]
