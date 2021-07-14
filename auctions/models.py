from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.CharField(max_length=120)
    # Digits include the digits after the decimal point, so make sure it is sufficient.
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    photo = models.ImageField(upload_to='images')
    category = models.CharField(max_length=50)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.listing} for sale by {self.user} - ${self.price}"

class Bid(models.Model):
    bidding_user = models.ForeignKey(User, on_delete=models.CASCADE)
    bidded_item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Bid {self.id}: Bid of ${self.bid_price} was placed by {self.bidding_user} on {self.bidded_item}."

class Comment(models.Model):
    user_commenting = models.ForeignKey(User, on_delete=models.CASCADE)
    commented_on = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user_commenting} commented: {self.comment}"

class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
