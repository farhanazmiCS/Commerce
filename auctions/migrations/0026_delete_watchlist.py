# Generated by Django 3.2.4 on 2021-07-14 03:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0025_watchlist'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Watchlist',
        ),
    ]
