# Generated by Django 3.1.7 on 2021-03-02 18:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20210226_1455'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TicketOrder',
        ),
    ]
