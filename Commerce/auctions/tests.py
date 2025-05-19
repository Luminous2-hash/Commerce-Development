from django.test import TestCase
# models
from auctions.models import User, UserProfile, Auction, Bid, Comment
# modules
from base64 import b64decode
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import model_to_dict
from django.urls import reverse

# An image generator for imagefield
class ImageGenerator:
    def __init__(self):
        self.image_bin = b64decode("R0lGODdhAQABAPAAAP8AAAAAACwAAAAAAQABAAACAkQBADs=")
        self.image_file = SimpleUploadedFile("image.gif", self.image_bin, "image/gif")

    def file(self):
        self.image_file.seek(0)
        return self.image_file

    def read(self):
        return self.image_bin

    def __str__(self):
        return self.image_file.name



class RegisterTest(TestCase):
    def setUp(self) -> None:
        self.register_url = reverse("register")
        self.PASSWORD = "NotSafe1234"

        # Initial User
        self.user = User.objects.create_user(
            username = "something",
            password = self.PASSWORD

        )
        # Initial Registration Data
        self.registeration_data = {
            "first_name": "first_name",
            "last_name": "last_name",
            "username": "username",
            "email": "someone@example.com",
            "password1": self.PASSWORD,
            "password2": self.PASSWORD,
        }

    def test_register_view(self):
        '''View Renders Correctly'''
        response = self.client.get(self.register_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "registration/register.html")
        self.assertIsNotNone(response.context["form"])

    def test_registering_normal(self):
        '''Tests View Register and logins the user'''
        users_count = User.objects.count()

        response = self.client.post(self.register_url, self.registeration_data)
        self.assertRedirects(response, reverse("index"), 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertIsNotNone(response.wsgi_request.user.userprofile)
        self.assertEqual(users_count+1, User.objects.count())
        
    def test_registering_errors(self):
        '''Tests View Register and logins the user negative cases'''
        user_count = User.objects.count()

        # Missing Required field case
        data = self.registeration_data.copy()
        data.pop("email")
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("email" ,response.context["form"].errors)

        # Mismatch password confirmation Check
        data = self.registeration_data.copy()
        data["password2"] = "12345678"
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("password2" ,response.context["form"].errors)

        # repeated username
        data = self.registeration_data.copy()
        data["username"] = self.user.username
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("username" ,response.context["form"].errors)

        # Password Strength
        data = self.registeration_data.copy()
        data["password1"] = data["password2"] = "1234567"
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("password2" ,response.context["form"].errors)
