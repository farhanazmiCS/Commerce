from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.listing} for sale by {self.user} - ${self.price}"

class Bid(models.Model):
    bidding_user = models.ForeignKey(User, on_delete=models.CASCADE)
    bidded_item = models.ForeignKey(Listing, on_delete=models.CASCADE)

class Comment(models.Model):
    user_commenting = models.ForeignKey(User, on_delete=models.CASCADE)
    commented_on = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)