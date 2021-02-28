# Generated by Django 3.1.7 on 2021-02-28 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0028_auto_20210228_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='bidding_on',
            field=models.CharField(choices=[('bidding_ready', '경매대기'), ('bidding', '경매중'), ('bidding_end', '경매종료')], default=0, help_text='경매여부', max_length=200),
        ),
    ]
