# Generated by Django 2.0.13 on 2021-01-22 16:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20210120_0302'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='bidding_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='경매시작일'),
        ),
    ]
