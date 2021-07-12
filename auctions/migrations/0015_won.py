# Generated by Django 3.2.4 on 2021-07-11 02:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_alter_listing_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Won',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auctions.listing')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('winner_price', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auctions.bid')),
            ],
        ),
    ]
