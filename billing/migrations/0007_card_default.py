# Generated by Django 2.0.13 on 2021-02-14 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_card'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='default',
            field=models.BooleanField(default=True),
        ),
    ]