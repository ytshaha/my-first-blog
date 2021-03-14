# Generated by Django 3.1.7 on 2021-03-11 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_auto_20210311_0235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='price_step',
            field=models.IntegerField(blank=True, choices=[(1000, '1,000 원'), (5000, '5,000 원'), (10000, '10,000 원')], default=5000, help_text='경매가격상승단위', null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='product_type',
            field=models.CharField(choices=[('normal', '일반물품'), ('bidding', '경매물품')], default='normal', max_length=20),
        ),
    ]
