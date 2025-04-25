from django.db import models

# User Management Requirements
from django.contrib.auth.models import User


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# UserProfile
class UserProfile(models.Model):
    # Relations
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Specs
    avatar = models.ImageField(default="default.png", upload_to="profile_images")
    bio = models.TextField(max_length=3000, blank=True)

    # Personal Contents
    watch_list = models.ManyToManyField("Auction", blank=True)
    
    def __str__(self):
        return f"Username: {self.user.username}"


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Text Choices For Auction's Categories
class AuctionCategories(models.TextChoices):
    APPAREL_AND_ACCESSORIES = "1", "Apparel and Accessories"
    CONSUMER_ELECTRONICS = "2", "Consumer Electronics"
    HOME_AND_KITCHEN_APPLIANCES = "3", "Home and Kitchen Appliances"
    HEALTH_AND_BEAUTY = "4", "Health and Beauty"
    FURNITURE_AND_DECOR = "5", "Furniture and Decor"
    SPORTS_AND_FITNESS = "6", "Sports and Fitness"
    BOOKS_AND_MEDIA = "7", "Books and Media"
    TOYS_AND_GAMES = "8", "Toys and Games"
    FOOD_AND_BEVERAGE = "9", "Food and Beverage"
    AUTO_AND_PARTS = "10", "Auto and Parts"
    OTHER = "11", "Other or Uncategorized"


# Text Choices For Auction's Status
class AuctionStatus(models.TextChoices):
    ACTIVE = "A", "Active"
    DEACTIVE = "D", "Deactive"
    CLOSED = "C", "Closed"


class Auction(models.Model):
    """Model definition for Auction."""

    # Specification
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    picture = models.ImageField(default="auction.png", upload_to="auction_images")
    price = models.FloatField()
    category = models.CharField(
        choices=AuctionCategories, default=AuctionCategories.OTHER
    )
    status = models.CharField(choices=AuctionStatus, default=AuctionStatus.ACTIVE)

    # Relations
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    top_bid = models.ForeignKey("Bid", blank=True, null=True, on_delete=models.SET_NULL)
        

    class Meta:
        """Meta definition for Auction."""
        ordering = ("date")
        
        verbose_name = "Auction"
        verbose_name_plural = "Auctions"
    
    def __str__(self):
        return f"{self.name}: {self.price}"

    # Updates top_bid and price for every higher bid
    def top_bid_handler(self, new_bid):
        if not self.price or new_bid.price > self.price:
            self.price = new_bid.price
            self.top_bid = new_bid
            self.save()
            
            
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Bid(models.Model):
    '''Model definition for Bid.'''
    
    # Specification
    date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    
    # Relations
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bid_auction")
    
    class Meta:
        '''Meta definition for Bid.'''
        ordering = ("price")

        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'

    def __str__(self):
        return f"{self.auction.name}: {self.price}"


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''    
class Comment(models.Model):
    '''Model definition for Comment.'''

    # Specification
    date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=600)
    
    # Relations
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    
    
    
    class Meta:
        '''Meta definition for Comment.'''
        ordering = ("date")

        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"{self.commenter.username}: {self.text}"