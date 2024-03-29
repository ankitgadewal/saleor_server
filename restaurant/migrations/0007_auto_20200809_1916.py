# Generated by Django 3.1 on 2020-08-09 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0006_auto_20200809_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='dish_images'),
        ),
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.CharField(choices=[('250gm', '250gm'), ('500gm', '500gm'), ('1kg', '1kg'), ('1', '1')], max_length=20),
        ),
    ]
