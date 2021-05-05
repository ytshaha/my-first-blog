# Generated by Django 3.1.7 on 2021-05-05 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0023_auto_20210503_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='product_type',
            field=models.CharField(choices=[('normal', '상시상품구매'), ('bidding', '경매상품구매'), ('ticket', '경매티켓구매'), ('rental', '렌탈상품구매')], default='bidding', max_length=20),
        ),
    ]