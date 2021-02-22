# Generated by Django 3.1.7 on 2021-02-21 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketCart',
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
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.CharField(blank=True, max_length=40)),
                ('update', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('unused', 'UNUSED'), ('activate', 'ACTIVATE'), ('used', 'USED')], default='unused', max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('bidding_success', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
