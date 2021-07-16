from django.urls import path

from . import views

from . import models

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="create"),
    path("listing/<int:inputListing>", views.view_listing, name="listing"),
    path("bid/<int:inputListing>", views.bid, name="bid"),
    path("won", views.won_listing, name="won"),
    path("categories", views.category, name="categories"),
    path("categories/<str:category>", views.category_results, name="category"),
    path("addwatchlist", views.add_to_watchlist, name="add"),
    path("removewatchlist", views.remove_from_watchlist, name="remove"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<int:inputListing>", views.comment, name="comment")
]
