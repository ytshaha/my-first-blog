# Generated by Django 2.0.13 on 2021-02-17 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketorder',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='ticketorder',
            name='billing_profile',
        ),
        migrations.RemoveField(
            model_name='ticketorder',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='ticketorder',
            name='ticketlist',
        ),
        migrations.DeleteModel(
            name='TicketOrder',
        ),
    ]
