# Generated by Django 3.1.7 on 2021-02-24 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_emailactivation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
