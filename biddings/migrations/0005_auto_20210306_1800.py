# Generated by Django 3.1.7 on 2021-03-06 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0038_auto_20210302_2109'),
        ('biddings', '0004_bidding_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bidding',
            name='product',
        ),
        migrations.AddField(
            model_name='bidding',
            name='product_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='products.productitem'),
            preserve_default=False,
        ),
    ]
