# Generated by Django 3.1.7 on 2021-02-26 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_auto_20210224_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='bidding_on',
            field=models.CharField(default=0, help_text='경매여부', max_length=200),
        ),
    ]
