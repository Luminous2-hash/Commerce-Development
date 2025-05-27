import os
import shutil
import tempfile
from base64 import b64decode
from io import StringIO
from pathlib import Path

from auctions.models import Auction, User, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.forms import model_to_dict
from django.test import TestCase, override_settings
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
            username="something", password=self.PASSWORD
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
        """View Renders Correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "registration/register.html")
        self.assertIsNotNone(response.context["form"])

    def test_registering_normal(self):
        """Tests View Register and logins the user"""
        users_count = User.objects.count()

        response = self.client.post(self.register_url, self.registeration_data)
        self.assertRedirects(response, reverse("index"), 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertIsNotNone(response.wsgi_request.user.userprofile)
        self.assertEqual(users_count + 1, User.objects.count())

    def test_registering_errors(self):
        """Tests View Register and logins the user negative cases"""
        user_count = User.objects.count()

        # Missing Required field case
        data = self.registeration_data.copy()
        data.pop("email")
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("email", response.context["form"].errors)

        # Mismatch password confirmation Check
        data = self.registeration_data.copy()
        data["password2"] = "12345678"
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("password2", response.context["form"].errors)

        # repeated username
        data = self.registeration_data.copy()
        data["username"] = self.user.username
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("username", response.context["form"].errors)

        # Password Strength
        data = self.registeration_data.copy()
        data["password1"] = data["password2"] = "1234567"
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("password2", response.context["form"].errors)

        # invalid email format
        data = self.registeration_data.copy()
        data["email"] = "invalid@domain"
        response = self.client.post(self.register_url, data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(user_count, User.objects.count())
        self.assertIn("email", response.context["form"].errors)


class UserprofileTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # default.png for default avatar
        default_path = os.path.join(tempfile.gettempdir(), "default.png")
        with open(default_path, "w") as file:
            file.write("I'm The Default Image!")

    def setUp(self):
        self.PASSWORD = "NotSafe1234"
        self.user = User.objects.create_user(
            username="username", password=self.PASSWORD
        )
        self.userprofile = UserProfile.objects.get(user=self.user)
        self.userprofile_view_url = reverse("userprofile")

        self.auction = Auction.objects.create(
            name="test_auction",
            price=1.0,
            owner=self.user,
        )
        self.userprofile.watch_list.add(self.auction)

    def test_userprofile_missing_returns_404(self):
        """Tests Absence Of UserProfile"""
        self.userprofile.delete()
        self.client.login(username=self.user.username, password=self.PASSWORD)
        response = self.client.get(self.userprofile_view_url)
        self.assertEqual(404, response.status_code)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_userprofile_get(self):
        """Tests User Profile Works As Expected"""
        # Populating UserProfile
        self.userprofile.bio = "Test Bio"
        self.userprofile.save()
        # LogIn the user and request
        self.client.login(username=self.user.username, password=self.PASSWORD)
        response = self.client.get(self.userprofile_view_url)
        # unit tests
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "userprofile.html")
        self.assertEqual(self.userprofile.bio, response.context["form"].initial["bio"])
        self.assertEqual(
            self.userprofile.avatar.name, response.context["form"].initial["avatar"]
        )
        self.assertTrue(
            response.context["watch_list_objects"].filter(id=self.auction.id).exists()
        )
        # behavioral tests
        self.assertContains(response, self.userprofile.bio)
        self.assertContains(response, self.userprofile.avatar.name)
        self.assertContains(response, self.auction.name)
        self.assertContains(
            response, reverse("watch_list", args=[self.auction.id, "delete"])
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_userprofile_post(self):
        # LogIn The User
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Data For Post Test
        image = ImageGenerator()
        data = {"avatar": image.file(), "bio": "BIO"}
        # POST Request
        response = self.client.post(self.userprofile_view_url, data, follow=True)
        # * Tests
        self.assertRedirects(response, reverse("userprofile"))
        messages = [str(message) for message in response.context["messages"]]
        self.assertIn("Your Profile Updated Successfully!", messages)
        self.userprofile.refresh_from_db()
        # - Updated Objects
        self.assertEqual(self.userprofile.avatar.read(), image.read())
        self.assertEqual(self.userprofile.bio, data["bio"])
        # - Updated Form
        self.assertEqual(
            self.userprofile.avatar.name, response.context["form"].initial["avatar"]
        )
        self.assertEqual(self.userprofile.bio, response.context["form"].initial["bio"])

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_negative_userprofile_post(self):
        # LogIn The User
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Data with bigger bio for negative Test
        data = {
            "avatar": SimpleUploadedFile(
                "picture.jpeg", b64decode("MQ=="), "image/jpeg"
            ),
            # max_lentght=300
            "bio": "h" * 301,
        }
        # Saving Old UserProfile
        old_userprofile = model_to_dict(self.userprofile)
        # POST Request
        response = self.client.post(self.userprofile_view_url, data, follow=True)
        # * Tests
        self.assertEqual(200, response.status_code)
        messages = [str(message) for message in response.context["messages"]]
        self.assertIn(
            "There Was An Issue with your submission. Please review the form and try again.",
            messages,
        )
        self.assertIn("bio", response.context["form"].errors)
        self.assertIn("avatar", response.context["form"].errors)
        # - Checking DataBase didn't get update
        self.userprofile.refresh_from_db()
        self.assertDictEqual(old_userprofile, model_to_dict(self.userprofile))


class CleanUpManagementCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        permission = 0o777

        # Creates an empty path for test files
        cls.default_path = Path(tempfile.gettempdir()).joinpath("cleanup")
        if cls.default_path.exists():
            shutil.rmtree(cls.default_path)
        cls.default_path.mkdir(mode=permission, parents=True, exist_ok=True)

        # default path for auction_images
        cls.auction_images_path = cls.default_path.joinpath("auction_images")
        cls.auction_images_path.mkdir(mode=permission, parents=True, exist_ok=True)
        # default path for profile_avatars
        cls.profile_images_path = cls.default_path.joinpath("profile_images")
        cls.profile_images_path.mkdir(mode=permission, parents=True, exist_ok=True)

        cls.file_number = 12

        # Temp files for Test
        for file_num in range(cls.file_number):
            with open(
                cls.auction_images_path.joinpath(f"file{file_num}.png"), "w"
            ) as f:
                f.write(f"I'm the file number {file_num}")

            with open(
                cls.profile_images_path.joinpath(f"file{file_num}.png"), "w"
            ) as f:
                f.write(f"I'm the file number {file_num}")

    @override_settings(MEDIA_ROOT=Path(tempfile.gettempdir()).joinpath("cleanup"))
    def setUp(self):
        # Database values for Test
        image = ImageGenerator()
        self.user = User.objects.create_user(
            username="username", password="NotSafe1234"
        )
        self.userprofile = UserProfile.objects.last()
        self.userprofile.avatar = image.file()
        self.userprofile.save()
        self.auction = Auction.objects.create(
            owner=self.user, name="auction", picture=image.file(), price=1.1
        )

    @override_settings(MEDIA_ROOT=Path(tempfile.gettempdir()).joinpath("cleanup"))
    def test_clean_up_management_command(self):
        # Calling cleanup to cleanUp and assertign the output for removed images
        output = StringIO()
        call_command("cleanup", "--yes", stdout=output)
        self.assertIn(
            f"Cleaned Up {self.file_number * 2} abundant images", output.getvalue()
        )
        # Calling cleanup to see everything is cleaned up
        output = StringIO()
        call_command("cleanup", "--yes", stdout=output)
        self.assertIn("Already cleanedUp nothing todo!", output.getvalue())
        # Checking for not abondant files
        auction_images = tuple(image for image in self.auction_images_path.iterdir())
        profile_images = tuple(image for image in self.profile_images_path.iterdir())

        self.assertEqual(1, len(auction_images))
        self.assertEqual(1, len(profile_images))
        self.assertIn(Path(self.auction.picture.path), auction_images)
        self.assertIn(Path(self.userprofile.avatar.path), profile_images)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.default_path, ignore_errors=True)
