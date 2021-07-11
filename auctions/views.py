from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def createlisting(request): 
    if request.method == "GET":
        return render(request, "auctions/createlisting.html")

    elif request.method == "POST":

        listing_name = request.POST["listing"]
        listing_price = float(request.POST["price"])
        listing_description = request.POST["textfield"]
        image = request.FILES["imagefield"]

    try:
        add_listing = Listing(user=request.user, listing=listing_name, price=listing_price, description=listing_description, photo=image)
        add_listing.save()
        
    except IntegrityError:
        return render(request, "auctions/createlisting.html", {
            "message": "Something went wrong."
        })

    return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    pass

@login_required
def categories(request):
    pass

def view_listing(request, inputListing):
    return render(request, "auctions/listing.html", {
        "listings": Listing.objects.filter(id=inputListing)
    })

@login_required
def bid(request, inputListing):
    if request.method == "GET":
        return render(request, "auctions/bid.html", {
            "listings": Listing.objects.filter(id=inputListing)
        })
    elif request.method == "POST":
        bid_price = float(request.POST["bid"])
        for listing in Listing.objects.filter(id=inputListing):
            current_price = float(listing.price)

        if bid_price <= current_price:
            return render(request, "auctions/bid.html", {
                "listings": Listing.objects.filter(id=inputListing),
                "error_message": "Your bid needs to be higher than the starting price."
            })
        else:
            for listing in Listing.objects.filter(id=inputListing):
                listing.price = bid_price
                listing.save()
            return redirect(f'/listing/{inputListing}')