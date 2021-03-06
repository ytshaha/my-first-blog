# Generated by Django 3.1.7 on 2021-03-30 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_customer_request'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='shipping_total',
            new_name='shipping_cost',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('created', 'Created'), ('paid', 'Paid'), ('shipping', 'Shipping'), ('shipped', 'Shipped'), ('refunded', 'Refunded'), ('cancel', 'Cancel')], default='created', max_length=120),
        ),
    ]
