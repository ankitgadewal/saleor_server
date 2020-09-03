# Generated by Django 3.1 on 2020-09-03 13:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0039_auto_20200903_1923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='start_date',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
