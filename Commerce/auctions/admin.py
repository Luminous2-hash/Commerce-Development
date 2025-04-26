from django.contrib import admin

from auctions.models import UserProfile, Auction, Bid, Comment

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("date", "name", "price", "status", "category")

@admin.register(Bid)    
class BidAdmin(admin.ModelAdmin):
    list_display = ("date", "bidder", "auction")
    
@admin.register(Comment)    
class Comment(admin.ModelAdmin):
    list_display = ("date", "commenter", "auction")
    