# Generated by Django 3.1.7 on 2021-02-21 14:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0059_auto_20210221_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 21, 14, 39, 48, 289328, tzinfo=utc)),
        ),
    ]
