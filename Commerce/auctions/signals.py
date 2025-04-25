# UserProfile Creation Response Requirements
from auctions.models import UserProfile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Userprofile Creation Response


@receiver(post_save, sender=User)
def userprofile_creator(sender, **kwargs):
    # Prevents Creating UserProfile from fixture.
    if kwargs.get("created") and not kwargs.get("raw"):
        user = kwargs.get("instance")

        # Creates UserProfile If Not Created Yet
        UserProfile.objects.get_or_create(user=user)
