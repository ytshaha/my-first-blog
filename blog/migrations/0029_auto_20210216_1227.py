# Generated by Django 2.0.13 on 2021-02-16 03:27

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0028_auto_20210216_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 16, 3, 27, 51, 72095, tzinfo=utc)),
        ),
    ]