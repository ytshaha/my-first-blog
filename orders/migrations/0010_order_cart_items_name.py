# Generated by Django 3.1.7 on 2021-04-10 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_auto_20210403_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart_items_name',
            field=models.CharField(blank=True, max_length=210, null=True),
        ),
    ]