from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment, Winner

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_closed=False)
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
            "message": "Missing Fields."
        })

    return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    pass

@login_required
def categories(request):
    pass

@login_required
def view_listing(request, inputListing):
    listing = Listing.objects.filter(id=inputListing)    
    # Check if the logged on user is the owner of the listing, if yes, allow the user to close the listing and declare
    # the highest bidder the winner
    for l in listing:
        if l.user == request.user:
            # If button is pressed, close the listing
            if request.method == "POST":
                try:
                    # Close the listing
                    l.is_closed = True
                    l.save()
                    # Retrieve all bids with the same listing id, and check for the highest
                    bids_list = Bid.objects.filter(bidded_item=inputListing)
                    # The '-' symbol denotes sorting in descending order.
                    bids_list = bids_list.order_by('-bid_price')
                    # Retrieve the highest bidder
                    winner = bids_list[0].bidding_user
                    # Save the winner into the Winner model
                    set_winner = Winner(user=winner, listing=Listing.objects.get(id=inputListing))
                    set_winner.save()
                # Raise exception if no bidders
                except:
                    return render(request, "auctions/error.html", {
                        "error_message": "No bidders.",
                        "listings": Listing.objects.filter(id=inputListing),
                        "comments": Comment.objects.filter(commented_on=inputListing)
                    })
                # Return a page that indicates that the listing is closed
                return render(request, "auctions/closedlisting.html", {
                    "message": "This listing is closed.",
                    "listings": Listing.objects.filter(id=inputListing),
                    "winner": winner,
                    "comments": Comment.objects.filter(commented_on=inputListing)
                })
            else:
                # Load the listing page for the original poster
                return render(request, "auctions/userlisting.html", {
                    "listings": Listing.objects.filter(id=inputListing),
                    "comments": Comment.objects.filter(commented_on=inputListing)
                })
        else:
            if request.method == "POST":
                retrieve_comment = request.POST["comment"]
                user = request.user
                insert_values = Comment(user_commenting=user, commented_on_id=inputListing, comment=retrieve_comment)
                insert_values.save()
                return render(request, "auctions/listing.html", {
                    "listings": Listing.objects.filter(id=inputListing),
                    "comments": Comment.objects.filter(commented_on=inputListing)
                })
            else:
                # Load the listing page for viewers to bid
                return render(request, "auctions/listing.html", {
                "listings": Listing.objects.filter(id=inputListing),
                "comments": Comment.objects.filter(commented_on=inputListing)
                })

@login_required
def bid(request, inputListing):
    if request.method == "GET":
        return render(request, "auctions/bid.html", {
            "listings": Listing.objects.filter(id=inputListing)
        })
    elif request.method == "POST":
        try:
            get_price = request.POST["bid"]
            bid_price = float(get_price)
        except ValueError:
            return render(request, "auctions/bid.html", {
                "listings": Listing.objects.filter(id=inputListing),
                "error_message": "Enter a numerical value."
            })
        for listing in Listing.objects.filter(id=inputListing):
            current_price = float(listing.price)

        if bid_price <= current_price:
            return render(request, "auctions/bid.html", {
                "listings": Listing.objects.filter(id=inputListing),
                "error_message": "Your bid needs to be higher than the starting price."
            })
        else:

            add_bid = Bid(bidding_user=request.user, bidded_item=Listing.objects.get(id=inputListing), bid_price=bid_price)
            add_bid.save()

            for listing in Listing.objects.filter(id=inputListing):
                listing.price = bid_price
                listing.save()

            return redirect(f'/listing/{inputListing}')