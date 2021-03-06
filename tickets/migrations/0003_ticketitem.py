# Generated by Django 3.1.7 on 2021-03-02 18:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tickets', '0002_delete_ticketcart'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtotal', models.IntegerField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('sale_ratio', models.DecimalField(decimal_places=1, default=0, help_text='할인율', max_digits=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('tickets_type', models.IntegerField(choices=[(1, 1), (3, 3), (5, 5), (10, 10), (20, 20), (30, 30)], default=0)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
