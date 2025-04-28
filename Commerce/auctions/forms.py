# Form Model Requirements
from django import forms
from django.db.models import Max, Min

# Custom UserCreationForm Requirements
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Models
from auctions.models import UserProfile, Auction, AuctionCategories, AuctionStatus


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
    email = forms.EmailField(max_length=30, required=True, help_text="name@example.com")

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )


# UserProfile Form
UserProfileForm = forms.modelform_factory(
    UserProfile,
    fields=("avatar", "bio"),
    widgets={
        "avatar": forms.widgets.FileInput(attrs={"accept": "image/*"}),
        "bio": forms.widgets.Textarea(attrs={"rows": "6", "cols": "30"}),
    },
    labels={"avatar": "Edit Avatar"},
)

# Auction Add or Edit Form
AuctionForm = forms.modelform_factory(
    Auction, fields=("name", "description", "picture", "price", "category", "status")
)


def add_empty_choice(choice_model):
    """
    Adds an "empty" choice to a TextChoices class.

    Args:
        choice_model (TextChoices subclass): A class that defines choices for a Django model field.

    Returns:
        list: A list of tuples consisting of an empty choice ('', 'ALL') followed by the original choices.
    """
    return [("", "ALL Options")] + list(choice_model.choices)


# Auctions Listing Filters
class AuctionsListingFiltersForm(forms.Form):
    max_venues_price = Auction.objects.aggregate(Max("price")).get("price__max", 0)
    min_venues_price = Auction.objects.aggregate(Min("price")).get("price__min", 0)

    category = forms.ChoiceField(
        required=False,
        choices=add_empty_choice(AuctionCategories),
        widget=forms.RadioSelect(attrs={"onchange": "this.form.submit()"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=add_empty_choice(AuctionStatus),
        widget=forms.RadioSelect(attrs={"onchange": "this.form.submit()"}),
    )
    start_price = forms.FloatField(
        required=False,
        initial=min_venues_price,
        max_value=max_venues_price,
        min_value=min_venues_price,
    )
    end_price = forms.FloatField(
        required=False,
        initial=max_venues_price,
        max_value=max_venues_price,
        min_value=min_venues_price,
    )

    def clean(self):
        super().clean()

        # # Price Range Validation
        # clean_date = self.cleaned_data
        # start_price = clean_date.get("start_price", 0)
        # end_price = clean_date.get("end_price", 0)

        # if start_price > end_price:
        #     raise forms.ValidationError("Start Price Can't Be Higher Than End Price")
