# Generated by Django 3.1.7 on 2021-02-28 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_auto_20210228_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='number',
            field=models.CharField(blank=True, help_text='상품관리용코드', max_length=10, null=True, unique=True),
        ),
    ]