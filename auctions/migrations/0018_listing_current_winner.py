# Generated by Django 3.2.4 on 2021-07-11 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_listing_is_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_winner',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
