from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator

# Models
from auctions.models import Auction, AuctionCategories, AuctionStatus

# Forms
from auctions.forms import UserProfileForm, UserRegisterForm, AuctionForm, AuctionsListingFiltersForm

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


# Index View
def index(request):
    '''_summary_
    Main Page
    Queries all auctions Then Caps Them at 6 Results and then renders them.
    '''
    dflt_items_count = 6
    
    auctions = Auction.objects.filter(status=AuctionStatus.ACTIVE)

    data = {
        "auctions_count": auctions.count(),
        "auctions": auctions[:dflt_items_count],
    }
    return render(request, "index.html", data)

# Auction View
def auction(request, auction_id):
    '''_summary_
    
    Retrives the auction object based on it's ID and
    renders it to auction page.
    '''
    auction_obj = get_object_or_404(Auction, id=auction_id)
    
    data = {
        "auction": auction_obj,
    }
    
    return render(request, "auction.html", data)

# Auction Management
@login_required
def auction_management(request, auction_id=0):
    '''_summary_

    View for managing auctions. Allows user to create or edit auctions.
    - if auction_id is provided, the view process the form submission.
    - if the request method is GET, the view displays the form to create or edit an auction.
    '''
    
    # concludes edit False or True
    edit = auction_id != 0
    
    # Form Initializing for edit or add mode
    if edit:
        auction_obj = get_object_or_404(Auction, id=auction_id, owner=request.user)
        form = AuctionForm(instance=auction_obj)
    else:
        form = AuctionForm()
    
    # Adds or Edit Auction
    if request.method == "POST":
        if edit:
            form = AuctionForm(request.POST, request.FILES, instance=auction_obj)
        else:
            form = AuctionForm(request.POST, request.FILES)
        
        if form.is_valid():
            auction_instance = form.save(commit=False)
            
            if not edit:
                auction_instance.owner = request.user
            
            auction_instance.save()
            return redirect(auction, auction_id=auction_instance.id)
        else:
            messages.error(request, "Processing Your Form Submission Failed!")
            
    data = {
        "form": form
    }
    return render(request, "auction_management.html", data)

# Categories View
def categories(request):
    '''_summary_
    Displays Categories
    Retrives AuctionCategories choices and renders them
    '''
    auction_categories = AuctionCategories.choices
    
    data = {
        "auction_categories": auction_categories,
    }
    
    return render(request, "categories.html", data)

# Listing View
def listing(request):
    form = AuctionsListingFiltersForm()
    auctions = Auction.objects.all()
    
    # Handles The Filters
    if request.GET:
        form = AuctionsListingFiltersForm(request.GET)
        if form.is_valid():
        
            # all the filters dictionary    
            filters = dict()
            
            # filters
            category = form.cleaned_data.get('category', None)
            if category:
                filters['category__exact'] = category
                
            status = form.cleaned_data.get('status', None)
            print(status)
            if status:
                filters['status__exact'] = status
                
            start_price = form.cleaned_data.get('start_price', None)
            end_price = form.cleaned_data.get('end_price', None)
            
            if start_price and end_price:
                filters['price__gte'] = start_price
                filters['price__lte'] = end_price
                
            # Querying Auctions With User Associated Filters
            auctions = auctions.filter(**filters)
    
    # To handle dynamic per_page_number and page_number
    if auctions.exists():
        # Defaults and Query initialiation
        dflt_per_page_number = 12
        dflt_page_number = 1

        # Get user prefrence for items per page, default to 12, cap at total count
        per_page_number = request.GET.get("per_page_number", dflt_per_page_number)

        try:
            per_page_number = int(per_page_number)
        except ValueError:
            per_page_number = dflt_per_page_number

        if per_page_number > auctions.count():
            per_page_number = auctions.count()

        # Set up paginator and fetch user-selected page, default to 1, cap at total
        paginator = Paginator(auctions, per_page_number)
        page_number = request.GET.get("page", dflt_page_number)

        try:
            page_number = int(page_number)
        except ValueError:
            page_number = dflt_page_number

        if page_number < dflt_page_number:
            page_number = dflt_page_number
        elif page_number > paginator.num_pages:
            page_number = paginator.num_pages

        page = paginator.get_page(page_number)
    
    # If No Auctions
    else:
        page = auctions
        
    data = {
        "page": page,
        "form": form,
    }
    
    return render(request, "listing.html", data)