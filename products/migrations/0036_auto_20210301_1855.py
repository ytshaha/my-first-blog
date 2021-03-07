# Generated by Django 3.1.7 on 2021-03-01 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0035_auto_20210301_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='amount',
            field=models.IntegerField(default=0, help_text='판매수량(경매 or 일반)'),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]