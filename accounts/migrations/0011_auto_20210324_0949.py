# Generated by Django 3.1.7 on 2021-03-24 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_registerticket_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='4~20글자 사이로 지정하십시오.', max_length=20, unique=True),
        ),
    ]
