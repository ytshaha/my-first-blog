# Generated by Django 3.1.7 on 2021-05-05 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_auto_20210411_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_rental',
            field=models.BooleanField(default=False),
        ),
    ]
