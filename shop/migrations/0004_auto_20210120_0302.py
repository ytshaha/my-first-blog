# Generated by Django 2.0.13 on 2021-01-19 18:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20210118_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='카테고리명', max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='published_date',
        ),
        migrations.AddField(
            model_name='product',
            name='limit_price',
            field=models.PositiveIntegerField(default=0, help_text='경매한도가격'),
        ),
        migrations.AddField(
            model_name='product',
            name='start_price',
            field=models.PositiveIntegerField(default=0, help_text='경매시작가격'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(help_text='브랜드명', max_length=200),
        ),
        migrations.AlterField(
            model_name='brand',
            name='website',
            field=models.CharField(blank=True, help_text='홈페이지', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='amount',
            field=models.IntegerField(default=0, help_text='수량'),
        ),
        migrations.AlterField(
            model_name='product',
            name='bidding',
            field=models.BooleanField(default=False, help_text='경매여부'),
        ),
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(help_text='브랜드명', on_delete=django.db.models.deletion.CASCADE, to='shop.Brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='물품생성일'),
        ),
        migrations.AlterField(
            model_name='product',
            name='info',
            field=models.TextField(blank=True, help_text='정보', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='number',
            field=models.CharField(blank=True, help_text='상품관리용코드', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product',
            field=models.CharField(help_text='상품명', max_length=200),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=True, help_text='카테고리', on_delete=django.db.models.deletion.CASCADE, to='shop.Category'),
            preserve_default=False,
        ),
    ]
