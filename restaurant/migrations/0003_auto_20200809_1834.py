# Generated by Django 3.1 on 2020-08-09 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0002_item_veg_or_nonveg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='veg_or_nonveg',
            field=models.CharField(choices=[('Nonveg', 'N'), ('Veg', 'V')], max_length=20),
        ),
    ]
