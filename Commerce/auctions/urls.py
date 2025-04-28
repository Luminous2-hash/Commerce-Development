from django.urls import path

from auctions import views

urlpatterns = [
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("edit_auction/<int:auction_id>", views.auction_management, name="edit_auction"),
    path("add_auction/", views.auction_management, name="add_auction"),
    path("categories/", views.categories, name="categories"),
    path("listing/", views.listing, name="listing")
]
