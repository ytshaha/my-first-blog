# Generated by Django 3.1.7 on 2021-04-04 09:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0016_auto_20210404_0043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billingprofile',
            old_name='customer_id',
            new_name='customer_uid',
        ),
    ]
