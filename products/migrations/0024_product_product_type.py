# Generated by Django 3.1.7 on 2021-02-23 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_auto_20210220_0651'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('normal', '상시상품구매'), ('bidding', '경매상품구매')], default='bidding', max_length=100),
        ),
    ]
