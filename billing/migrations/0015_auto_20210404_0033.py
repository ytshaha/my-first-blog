# Generated by Django 3.1.7 on 2021-04-03 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0014_auto_20210404_0029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charge',
            old_name='customer_id',
            new_name='customer_uid',
        ),
    ]
