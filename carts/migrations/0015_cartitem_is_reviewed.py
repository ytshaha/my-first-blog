# Generated by Django 3.1.7 on 2021-03-13 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0014_auto_20210314_0147'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='is_reviewed',
            field=models.BooleanField(default=False),
        ),
    ]
