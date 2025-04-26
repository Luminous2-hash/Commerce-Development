from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages

# Models

# Forms
from auctions.forms import UserProfileForm, UserRegisterForm

# Auth
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


# User Registration View
def register(request):
    """_summary_
    view for handling User self-registeration

    This view process the form submission and creates new User

    If request method is GET, Displays the registration fomr
    If request method is POST, Validates the form and creates user
    """
    # User Creation
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Loging in the user
            login(request, user)
            return redirect("index")

    else:
        form = UserRegisterForm()

    data = {
        "form": form,
    }
    return render(request, "registration/register.html", data)


# User Profile View
@login_required
def userprofile(request):
    """_summary_

    Handles Display and Edit The UserProfile

    Checks for UserProfile to exist

    If request method is GET, Displays the UserProfile
    If request method is POST, Validates the form and updates the UserProfile
    """

    # Retrives UserProfile associated with request
    profile = getattr(request.user, "userprofile", None)
    if not profile:
        raise Http404("UserProfile Not Found!")

    # Handles Get Request
    if request.method == "GET":
        form = UserProfileForm(instance=profile)

    # Updates UserProfile
    elif request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Profile Updated Successfuly!")
            return redirect(userprofile)
        else:
            messages.error(
                request,
                "There Was An Issue with your submission. Please review the form and try again.",
            )

    data = {
        "form": form,
    }

    return render(request, "userprofile.html", data)


# Main Page
def index(request):
    return render(request, "base.html", {})
