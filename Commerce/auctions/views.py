from django.shortcuts import render
from django.contrib import messages

# Registeration Requirements
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm


def register(request):
    data = {
        "form": UserCreationForm
    }
    return render(request, "registration/register.html", data)

def index(request):
    messages.warning(request, "Hello It's Working")
    return render(request, "base.html", {})