# Generated by Django 2.0.13 on 2021-01-18 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='number',
            field=models.CharField(default=True, max_length=200),
            preserve_default=False,
        ),
    ]
