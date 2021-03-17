# Generated by Django 3.1.7 on 2021-03-15 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0042_auto_20210315_0439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='number',
            field=models.CharField(default=1, help_text='상품관리용코드', max_length=40, unique=True),
            preserve_default=False,
        ),
    ]
