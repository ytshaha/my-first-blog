# Generated by Django 2.0.13 on 2021-01-30 02:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20210130_0210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 30, 2, 57, 42, 636475, tzinfo=utc)),
        ),
    ]
