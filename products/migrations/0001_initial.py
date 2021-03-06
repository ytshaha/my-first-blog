# Generated by Django 2.0.13 on 2021-02-03 22:26

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='브랜드명', max_length=200)),
                ('website', models.CharField(blank=True, help_text='홈페이지', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='카테고리명', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(blank=True, help_text='상품관리용코드', max_length=10, null=True)),
                ('product', models.CharField(help_text='상품명', max_length=200)),
                ('start_price', models.PositiveIntegerField(default=0, help_text='경매시작가격')),
                ('limit_price', models.PositiveIntegerField(default=0, help_text='경매한도가격')),
                ('info', models.TextField(blank=True, help_text='정보', null=True)),
                ('amount', models.IntegerField(default=0, help_text='수량')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, help_text='물품생성일')),
                ('bidding', models.BooleanField(default=False, help_text='경매여부')),
                ('bidding_date', models.DateTimeField(default=django.utils.timezone.now, help_text='경매시작일')),
                ('image', models.ImageField(upload_to='shop/images')),
                ('brand', models.ForeignKey(help_text='브랜드명', on_delete=django.db.models.deletion.CASCADE, to='products.Brand')),
                ('category', models.ForeignKey(help_text='카테고리', on_delete=django.db.models.deletion.CASCADE, to='products.Category')),
            ],
        ),
    ]
