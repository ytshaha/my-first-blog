# Generated by Django 3.1.7 on 2021-04-03 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_auto_20210403_2313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='outcome',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='outcome_type',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='risk_level',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='seller_message',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='stripe_id',
        ),
    ]
