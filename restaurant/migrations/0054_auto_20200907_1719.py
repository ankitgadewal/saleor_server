# Generated by Django 3.1 on 2020-09-07 11:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('restaurant', '0053_auto_20200907_1128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='stripe_charge_id',
            new_name='charge_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='payment',
            name='bank_txn_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='checksum_hash',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_mode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
        ),
        migrations.DeleteModel(
            name='PaytmPayment',
        ),
    ]
