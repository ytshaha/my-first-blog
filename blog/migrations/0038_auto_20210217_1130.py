# Generated by Django 2.0.13 on 2021-02-17 02:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0037_auto_20210217_0542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 17, 2, 30, 14, 578420, tzinfo=utc)),
        ),
    ]
