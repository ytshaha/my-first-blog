# Generated by Django 3.1.7 on 2021-03-12 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20210313_0711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewimage',
            old_name='post',
            new_name='review',
        ),
    ]