# Generated by Django 3.1.7 on 2021-02-24 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_cartitem_price'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CartItemManager',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='subtotal',
            field=models.IntegerField(default=0, help_text='카트총액'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='price',
            field=models.PositiveIntegerField(default=0, help_text='단가'),
        ),
    ]