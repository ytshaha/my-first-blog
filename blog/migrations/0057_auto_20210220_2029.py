# Generated by Django 2.0.13 on 2021-02-20 11:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0056_auto_20210220_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 20, 11, 29, 26, 401135, tzinfo=utc)),
        ),
    ]
