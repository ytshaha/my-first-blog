# Generated by Django 3.1.7 on 2021-02-24 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_auto_20210224_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='subtotal',
            field=models.PositiveIntegerField(default=0, help_text='카트총액'),
        ),
    ]
