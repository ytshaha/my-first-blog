# Generated by Django 3.1.7 on 2021-03-07 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0011_cartitem_sale_ratio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='sale_ratio',
            field=models.DecimalField(decimal_places=1, default=0, help_text='할인율_자동계산필드', max_digits=100),
        ),
    ]
