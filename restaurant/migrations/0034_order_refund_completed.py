# Generated by Django 3.1 on 2020-09-03 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0033_order_order_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='refund_completed',
            field=models.BooleanField(default=False),
        ),
    ]