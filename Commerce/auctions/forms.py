# Form Model Requirements
from django import forms

# Custom UserCreationForm Requirements
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# User Register Form
class UserRegisterForm(UserCreationForm):
    # Below Fields Are blank=True in User Model
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.widgets.TextInput(attrs={"autofocus": True}),
        help_text="Max Character Is 30",
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text="Max Character Is 30",
    )
    email = forms.EmailField(max_length=30, required=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )
