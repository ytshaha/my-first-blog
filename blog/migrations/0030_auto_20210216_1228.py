# Generated by Django 2.0.13 on 2021-02-16 03:28

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0029_auto_20210216_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 16, 3, 28, 29, 727325, tzinfo=utc)),
        ),
    ]
