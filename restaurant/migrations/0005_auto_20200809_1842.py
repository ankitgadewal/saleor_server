# Generated by Django 3.1 on 2020-08-09 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0004_item_quanity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='quanity',
            new_name='quantity',
        ),
    ]
