# Generated by Django 3.1.7 on 2021-04-03 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_auto_20210403_2234'),
        ('billing', '0010_auto_20210307_1950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='billing_profile',
        ),
        migrations.AddField(
            model_name='charge',
            name='order_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.orderaddress'),
        ),
    ]
