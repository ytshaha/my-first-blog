# Generated by Django 2.0.13 on 2021-01-18 13:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20210117_0030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 18, 13, 37, 35, 964211, tzinfo=utc)),
        ),
    ]
