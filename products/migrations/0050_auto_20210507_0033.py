# Generated by Django 3.1.7 on 2021-05-06 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0049_auto_20210430_0808'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image1_link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='image2_link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='main_image_link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]