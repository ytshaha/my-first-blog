# Generated by Django 2.0.13 on 2021-02-14 22:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_auto_20210214_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 14, 22, 48, 59, 462545, tzinfo=utc)),
        ),
    ]
