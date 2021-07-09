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
    path("bid/<int:inputListing>", views.bid, name="bid")
]
