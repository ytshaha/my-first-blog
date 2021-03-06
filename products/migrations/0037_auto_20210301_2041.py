# Generated by Django 3.1.7 on 2021-03-01 11:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0036_auto_20210301_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='bidding_end_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='경매종료일', null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='bidding_on',
            field=models.CharField(blank=True, choices=[('bidding_ready', '경매대기'), ('bidding', '경매중'), ('bidding_end', '경매종료')], default=0, help_text='경매여부', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='bidding_start_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='경매시작일', null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='current_price',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='경매현재가격', null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='price_step',
            field=models.IntegerField(blank=True, default=5000, help_text='경매가격상승단위', null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='remain_bidding_time',
            field=models.CharField(blank=True, default=0, help_text='남은경매시간', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='start_price',
            field=models.PositiveIntegerField(blank=True, help_text='경매시작가격', null=True),
        ),
    ]
