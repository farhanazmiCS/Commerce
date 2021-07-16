from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment, Winner, Watchlist

# Defining a pre-defined list of categories
categories = ["Technology", "Clothing", "Vehicles", "Accessories", "Others"]

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

def createlisting(request): 
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "auctions/createlisting.html", {
                "category": categories
            })

        elif request.method == "POST":

            try:
                listing_name = request.POST["listing"]
                listing_price = float(request.POST["price"])
                listing_description = request.POST["textfield"]
                listing_category = request.POST["category"]
                image = request.FILES["imagefield"]
                add_listing = Listing(user=request.user, listing=listing_name, price=listing_price, category=listing_category, description=listing_description, photo=image)
                add_listing.save()
            
            except IntegrityError:
                return render(request, "auctions/createlisting.html", {
                    "message": "Missing Fields."
                })

            return HttpResponseRedirect(reverse("index"))
    else:
        return redirect("login")
    

def view_listing(request, inputListing):
    if request.user.is_authenticated:
        # Filters the listing, according to id. Returns one listing.
        listing = Listing.objects.filter(id=inputListing)    
        # Loop through the queryset(s)
        for l in listing:
            # If the owner of the listing matches the logged on user
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
                        # Declare the winner
                        winner = bids_list[0].bidding_user
                        # Save the winner into the Winner model
                        set_winner = Winner(user=winner, listing=Listing.objects.get(id=inputListing))
                        set_winner.save()
                        # Return a page that indicates that the listing is closed
                        return render(request, "auctions/closedlisting.html", {
                            "message": "This listing is closed.",
                            "listings": Listing.objects.filter(id=inputListing),
                            "winner": winner,
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count()
                        })
                    # Raise exception if no bidders
                    except:
                        # Condition for no bidders, load error.
                        return render(request, "auctions/error.html", {
                            "error_message": "No bidders.",
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing)
                        })
                # GET request method
                else:
                    if l.is_closed == True:
                        return render(request, "auctions/closedlisting.html", {
                            "message": "This listing is closed.",
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count()
                        })
                    else:
                        # Load the listing page for the original poster
                        return render(request, "auctions/userlisting.html", {
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count()
                        })
            # For viewers of listing (Not original poster)
            else:
                for l in listing:
                    # If listing is closed, prevent user from bidding.
                    if l.is_closed == True:
                        # Get the winner
                        winner = Winner.objects.get(user=request.user, listing=l)
                        winner = winner.user
                        # If the winner of the listing logs in the closed listing and won it, it now indicates so.
                        if winner == request.user:
                            return render(request, "auctions/closedlisting.html", {
                                "message": "This listing is closed.",
                                "you_won": "You have won this listing!",
                                "listings": Listing.objects.filter(id=inputListing),
                                "comments": Comment.objects.filter(commented_on=inputListing),
                                "bids": Bid.objects.filter(bidded_item=inputListing).count()
                            })
                        # For closed listings, where the logged on user is not the winner.
                        else:
                            return render(request, "auctions/closedlisting.html", {
                                "message": "This listing is closed.",
                                "listings": Listing.objects.filter(id=inputListing),
                                "comments": Comment.objects.filter(commented_on=inputListing),
                                "bids": Bid.objects.filter(bidded_item=inputListing).count()
                            })
                    else:
                        try:
                            # Attempt to retrieve QuerySet object from Watchlist
                            # If Watchlist listing matches with the viewed listing, viewed listing is in the user's watchlist
                            check_watchlist = Watchlist.objects.get(user=request.user, listing=inputListing)
                            if check_watchlist.listing_id == l.id:
                                return render(request, "auctions/listingdelete.html", {
                                    "listings": Listing.objects.filter(id=inputListing),
                                    "comments": Comment.objects.filter(commented_on=inputListing),
                                    "bids": Bid.objects.filter(bidded_item=inputListing).count()
                                })
                        except:
                            # When no QuerySet matches (Empty Queryset, nothing in watchlist), load listing.html and allow the user to add
                            # the listing into the watchlist
                            return render(request, "auctions/listing.html", {
                                "listings": Listing.objects.filter(id=inputListing),
                                "comments": Comment.objects.filter(commented_on=inputListing),
                                "bids": Bid.objects.filter(bidded_item=inputListing).count()
                            })
    # Redirect users who are not logged on      
    else:
        return redirect("login")


def bid(request, inputListing):
    if request.user.is_authenticated:
        if request.method == "GET":
            if not Watchlist.objects.filter(user=request.user, listing=inputListing):
                return render(request, "auctions/listing.html", {
                    "listings": Listing.objects.filter(id=inputListing),
                    "comments": Comment.objects.filter(commented_on=inputListing),
                    "bids": Bid.objects.filter(bidded_item=inputListing).count()
                })
            else:
                return render(request, "auctions/listingdelete.html", {
                    "listings": Listing.objects.filter(id=inputListing),
                    "comments": Comment.objects.filter(commented_on=inputListing),
                    "bids": Bid.objects.filter(bidded_item=inputListing).count()
                })
        elif request.method == "POST":
            try:
                get_price = request.POST["bid"]
                bid_price = float(get_price)

            except ValueError:
                if not Watchlist.objects.filter(user=request.user, listing=inputListing):
                    return render(request, "auctions/listing.html", {
                        "listings": Listing.objects.filter(id=inputListing),
                        "comments": Comment.objects.filter(commented_on=inputListing),
                        "bids": Bid.objects.filter(bidded_item=inputListing).count(),
                        "error_message": "Enter a numerical value."
                    })
                else:
                    return render(request, "auctions/listingdelete.html", {
                        "listings": Listing.objects.filter(id=inputListing),
                        "comments": Comment.objects.filter(commented_on=inputListing),
                        "bids": Bid.objects.filter(bidded_item=inputListing).count(),
                        "error_message": "Enter a numerical value."
                    })

            # Retrieve the current price
            for listing in Listing.objects.filter(id=inputListing):
                current_price = float(listing.price)

            # If query is empty
            if not Bid.objects.filter(bidded_item=inputListing):
                # If bid price is less than the current price, present an error
                if bid_price < current_price:
                    if not Watchlist.objects.filter(user=request.user, listing=inputListing):
                        return render(request, "auctions/listing.html", {
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count(),
                            "error_message": "Your bid needs to be equal or higher than the starting price."
                        })
                    else:
                        return render(request, "auctions/listingdelete.html", {
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count(),
                            "error_message": "Your bid needs to be equal or higher than the starting price."
                        })
                else:
                    # If bid price is EQUAL or HIGHER than the current price, save the bid
                    add_bid = Bid(bidding_user=request.user, bidded_item=Listing.objects.get(id=inputListing), bid_price=bid_price)
                    add_bid.save()
                
                    # Save the bid price into the listing
                    for listing in Listing.objects.filter(id=inputListing):
                        listing.price = bid_price
                        listing.save()

                    return redirect(f'/listing/{inputListing}')
                
            # If queryset does have bids present
            else:
                # Present an error if bid price is not more than current price
                if bid_price <= current_price:
                    if not Watchlist.objects.filter(user=request.user, listing=inputListing):
                        return render(request, "auctions/listing.html", {
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count(),
                            "error_message": "Your bid needs to be higher than the previous bid."
                        })
                    else:
                        return render(request, "auctions/listingdelete.html", {
                            "listings": Listing.objects.filter(id=inputListing),
                            "comments": Comment.objects.filter(commented_on=inputListing),
                            "bids": Bid.objects.filter(bidded_item=inputListing).count(),
                            "error_message": "Your bid needs to be higher than the previous bid."
                        })
                # Add the bid
                else:

                    add_bid = Bid(bidding_user=request.user, bidded_item=Listing.objects.get(id=inputListing), bid_price=bid_price)
                    add_bid.save()

                    for listing in Listing.objects.filter(id=inputListing):
                        listing.price = bid_price
                        listing.save()

                    return redirect(f'/listing/{inputListing}')
    else:
        return redirect("login")


def won_listing(request):
    if request.user.is_authenticated:
        # Returns me all the listings that the logged on user has won
        w = Winner.objects.filter(user=request.user)
        if not w:
            return render(request, "auctions/won.html", {
                "message": "You have not won any listing."
            })
        else:
            # Queries the "Listing" table, filters by the l
            return render(request, "auctions/won.html", {
                "listings_won": w
            })
    else:
        return redirect("login")


# Path to load the categories page
def category(request):
    if request.user.is_authenticated:
        return render(request, "auctions/categories.html", {
            "categories": categories
        })
    else:
        return redirect("login")


# Returns the listings in the requested category
def category_results(request, category):
    if request.user.is_authenticated:
        get_listing_category = Listing.objects.filter(category=category, is_closed=False)
        if not get_listing_category:
            return render(request, "auctions/index.html", {
                "no_listings": "This category has no listings!",
                "category": category
            })
        else:
            return render(request, "auctions/index.html", {
                "matched": get_listing_category,
                "category": category
            })
    else:
        return redirect("login")

def add_to_watchlist(request):
    if request.method == "POST":
        try:
            retrieve_listing_id = int(request.POST["listing_id"])
            add = Watchlist(user=request.user, listing_id=retrieve_listing_id)
            add.save()
        except:
            return render(request, "auctions/error.html", {
                "listings": Listing.objects.filter(id=retrieve_listing_id),
                "comments": Comment.objects.filter(commented_on=retrieve_listing_id),
                "error_message": "Could not add the listing into the watchlist.",
                "bids": Bid.objects.filter(bidded_item=retrieve_listing_id).count()
            })
        return redirect(f'listing/{retrieve_listing_id}')

def remove_from_watchlist(request):
    if request.method == "POST":
        try:
            retrieve_listing_id = int(request.POST["listing_id"])
            check = Watchlist.objects.get(user=request.user, listing_id=retrieve_listing_id)
            if check.listing_id == retrieve_listing_id:
                check.delete()
        except:
            return render(request, "auctions/error.html", {
                "listings": Listing.objects.filter(id=retrieve_listing_id),
                "comments": Comment.objects.filter(commented_on=retrieve_listing_id),
                "error_message": "Could not remove item from watchlist.",
                "bids": Bid.objects.filter(bidded_item=retrieve_listing_id).count()
            })
        return redirect(f'listing/{retrieve_listing_id}')
    
def watchlist(request):
    if request.user.is_authenticated:
        watchlist_listings = Watchlist.objects.filter(user=request.user)
        if not watchlist_listings:
            return render(request, "auctions/index.html", {
                "empty_watchlist": "Your watchlist is empty."
            })
        else:
            return render(request, "auctions/index.html", {
                "watchlist": watchlist_listings
            })
    else:
        return redirect("login")

def comment(request, inputListing):
    # For original lister
    op = Listing.objects.filter(id=inputListing, user=request.user)
    for o in op:
        if o.user_id == request.user:
            if request.method == "POST":
                retrieve_comment = request.POST["comment"]
                user = request.user
                insert_values = Comment(user_commenting=user, commented_on_id=inputListing, comment=retrieve_comment)
                insert_values.save()
                return redirect(f"/listing/{inputListing}")
            else:
                return render(request, "auctions/userlisting.html", {
                    "listings": Listing.objects.filter(id=inputListing),
                    "comments": Comment.objects.filter(commented_on=inputListing)
                })
    else:
        # For non-original listers
        if request.method == "POST":
            retrieve_comment = request.POST["comment"]
            user = request.user
            insert_values = Comment(user_commenting=user, commented_on_id=inputListing, comment=retrieve_comment)
            insert_values.save()
            return redirect(f"/listing/{inputListing}")
        else:
            return redirect(f"/listing/{inputListing}")