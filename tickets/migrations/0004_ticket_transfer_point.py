# Generated by Django 3.1.7 on 2021-03-04 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_ticketitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='transfer_point',
            field=models.BooleanField(default=False),
        ),
    ]