# Generated by Django 2.0.13 on 2021-02-04 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20210205_0447'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='product',
            new_name='title',
        ),
    ]
