# Generated by Django 3.1 on 2020-09-03 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0035_auto_20200903_1115'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='coupon',
            new_name='applied_coupon',
        ),
    ]