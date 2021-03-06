# Generated by Django 3.1.7 on 2021-04-03 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0008_order_shipping_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('address_line_1', models.CharField(max_length=120)),
                ('address_line_2', models.CharField(blank=True, max_length=120, null=True)),
                ('postal_code', models.CharField(max_length=120)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='final_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.orderaddress'),
        ),
    ]
