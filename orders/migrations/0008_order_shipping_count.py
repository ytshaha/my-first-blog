# Generated by Django 3.1.7 on 2021-03-30 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20210331_0410'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_count',
            field=models.IntegerField(default=0),
        ),
    ]