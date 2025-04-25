# UserProfile Creation Response Requirements
from auctions.models import UserProfile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Userprofile Creation Response

@receiver(post_save, sender=User)
def userprofile_creator(sender, **kwargs):
    
    # Prevents Creating UserProfile from fixture.
    if kwargs['created'] and not kwargs['raw']:
        user = kwargs['instance']
    
    try:
        # Checks For UserProfile existance
        # DjangoAdmin May Created Before
        UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user)