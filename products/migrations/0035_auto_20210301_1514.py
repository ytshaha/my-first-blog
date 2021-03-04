# Generated by Django 3.1.7 on 2021-03-01 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0034_auto_20210301_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='product_type',
            field=models.CharField(choices=[('normal', '상시상품구매'), ('bidding', '경매상품구매')], default='normal', max_length=20),
        ),
    ]
