# Generated by Django 3.2.4 on 2021-07-08 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_listing_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='bid_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
