<<<<<<< HEAD
# Generated by Django 3.2.4 on 2021-07-11 10:48
=======
# Generated by Django 3.2.4 on 2021-07-11 02:01
>>>>>>> close-listing-feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_listing_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='photo',
            field=models.ImageField(upload_to='images'),
        ),
    ]
