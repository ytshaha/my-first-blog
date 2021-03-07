# Generated by Django 3.1.7 on 2021-03-06 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biddings', '0005_auto_20210306_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='bidding',
            name='sale_ratio',
            field=models.DecimalField(decimal_places=1, default=0, help_text='할인율', max_digits=100),
        ),
    ]
