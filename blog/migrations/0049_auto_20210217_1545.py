# Generated by Django 2.0.13 on 2021-02-17 06:45

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0048_auto_20210217_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 17, 6, 45, 37, 66872, tzinfo=utc)),
        ),
    ]
