from django.db import models

# User Management Requirements
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    avatar = models.ImageField(default='default.png', upload_to='profile_images')
    bio = models.TextField(max_length=3000, blank=True)

    
    def __str__(self):
        return f"Username: {self.user.username}"
    
