# Generated by Django 2.0.13 on 2021-02-16 03:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_auto_20210216_1227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='bidding_date',
            new_name='bidding_start_date',
        ),
    ]