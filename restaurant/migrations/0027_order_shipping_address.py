# Generated by Django 3.1 on 2020-09-01 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0026_auto_20200814_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
