# Generated by Django 3.1.7 on 2021-03-17 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0046_productitem_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sizeoption',
            name='size',
        ),
        migrations.AddField(
            model_name='sizeoption',
            name='option',
            field=models.CharField(default=0, help_text='옵션', max_length=20),
        ),
        migrations.AlterField(
            model_name='sizeoption',
            name='amount',
            field=models.IntegerField(default=0, help_text='옵션별수량'),
        ),
    ]