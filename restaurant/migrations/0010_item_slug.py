# Generated by Django 3.1 on 2020-08-09 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0009_auto_20200809_2004'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
    ]
