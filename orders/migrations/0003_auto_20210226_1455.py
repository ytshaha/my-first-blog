# Generated by Django 3.1.7 on 2021-02-26 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210223_0552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ticketorder',
            name='shipping_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ticketorder',
            name='total',
            field=models.IntegerField(default=0),
        ),
    ]
