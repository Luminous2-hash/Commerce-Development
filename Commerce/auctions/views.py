from django.shortcuts import render, redirect
from django.contrib import messages

# Registeration Requirements
from django.contrib.auth import login
from auctions.forms import UserRegisterForm


def register(request):
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


# Main Page
def index(request):

    return render(request, "base.html", {})
