# Generated by Django 2.0.13 on 2021-02-15 22:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_auto_20210216_0714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 15, 22, 29, 20, 965823, tzinfo=utc)),
        ),
    ]
