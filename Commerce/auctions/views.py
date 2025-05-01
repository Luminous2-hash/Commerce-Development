from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator


# Models
from auctions.models import Auction, AuctionCategories, AuctionStatus, Bid, Comment

# Forms
from auctions.forms import (
    UserProfileForm,
    UserRegisterForm,
    AuctionForm,
    AuctionsListingFiltersForm,
)

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

    # Retrives Watch list
    watch_list_objects = profile.watch_list.all()

    data = {
        "watch_list_objects": watch_list_objects,
        "form": form,
    }

    return render(request, "userprofile.html", data)


# Index View
def index(request):
    """_summary_
    Main Page
    Queries all active auctions Then Caps Them at 6 Results and then renders them.
    """
    dflt_items_count = 6

    auctions = Auction.objects.filter(status=AuctionStatus.ACTIVE)

    data = {
        "auctions_count": auctions.count(),
        "auctions": auctions[:dflt_items_count],
    }
    return render(request, "index.html", data)


# Auction View
def auction(request, auction_id):
    """_summary_

    Retrives the auction object based on it's ID and
    renders it to auction page.
    """
    auction_obj = get_object_or_404(Auction, id=auction_id)
    comments = Comment.objects.filter(auction=auction_obj)[:10]
    data = {
        "comments": comments,
        "auction": auction_obj,
    }

    return render(request, "auction.html", data)


# Auction Management
@login_required
def auction_management(request, auction_id=0):
    """_summary_

    View for managing auctions. Allows user to create or edit auctions.
    - if auction_id is provided, the view process the form submission.
    - if the request method is GET, the view displays the form to create or edit an auction.
    """

    # concludes edit False or True
    edit = auction_id != 0

    # Form Initializing for edit or add mode
    if edit:
        auction_obj = get_object_or_404(Auction, id=auction_id, owner=request.user)

        # Auction Shouldn't be Closed
        if auction_obj.status == AuctionStatus.CLOSED:
            raise Http404("Can't Edit Closed Auction!")

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
            # Fills owner field for new auctions
            if not edit:
                auction_instance.owner = request.user
            auction_instance.save()
            return redirect(auction, auction_id=auction_instance.id)
        else:
            messages.error(request, "Processing Your Form Submission Failed!")

    data = {
        "form": form,
    }

    return render(request, "auction_management.html", data)


# Categories View
def categories(request):
    """_summary_
    Displays Categories
    Retrives AuctionCategories choices and renders them
    """
    auction_categories = AuctionCategories.choices

    data = {
        "auction_categories": auction_categories,
    }

    return render(request, "categories.html", data)


# Listing View
def listing(request):
    """__summary__
    Retrieves all auctions and applies filters based on the GET request parameters.

    Filters include category, status, and price range (start_price and end_price).
    Handles pagination dynamically based on user preferences for items per page and the current page.

    If no GET parameters are provided, renders the filter form and all auctions.
    If the QuerySet is empty, skips the pagination process and assigns an empty list to the page.
    """
    filter_form = AuctionsListingFiltersForm()
    auctions = Auction.objects.all()

    # Handles The Filters
    if request.GET:
        filter_form = AuctionsListingFiltersForm(request.GET)
        if filter_form.is_valid():
            # all the filters dictionary
            filters = dict()

            # filters
            category = filter_form.cleaned_data.get("category", None)
            if category:
                filters["category__exact"] = category

            status = filter_form.cleaned_data.get("status", None)
            if status:
                filters["status__exact"] = status

            start_price = filter_form.cleaned_data.get("start_price", None)
            end_price = filter_form.cleaned_data.get("end_price", None)

            if start_price:
                filters["price__gte"] = start_price
            if end_price:
                filters["price__lte"] = end_price

            # Querying Auctions With User Associated Filters
            auctions = auctions.filter(**filters)

    # To handle dynamic per_page_number and page_number
    # Halts The Pagination Process If No Auction
    if auctions.exists():
        # Defaults and Query initialiation
        dflt_per_page_number = 8
        dflt_page_number = 1

        # Get user prefrence for items per page, default to 12, cap at total count
        per_page_number = request.GET.get("per_page_number", dflt_per_page_number)

        try:
            per_page_number = int(per_page_number)
        except ValueError:
            per_page_number = dflt_per_page_number

        if per_page_number <= 0:
            per_page_number = dflt_per_page_number
        elif per_page_number > auctions.count():
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
        page = None

    data = {
        "page": page,
        "form": filter_form,
    }

    return render(request, "listing.html", data)


@login_required
def bid(request, auction_id=None):
    """__summary__
    Handles the bidding process for an auction.

    Raises Http404 if no auction ID is provided or the auction is not found.
    Retrieves price from POST request and converts it to float.
    Checks auction status to be active before processing the bid.
    Creates a new bid instance or updates the user's existing bid.
    Executes the auction's top_bid_handler method to validate and update the top bid and auction price.
    """

    # No Auction Provided Handler
    if not auction_id:
        raise Http404("Auction ID is required!")

    # Retrives Auction Object
    auction_obj = get_object_or_404(Auction, id=auction_id)

    # Checking Auction To be Active
    if auction_obj.status != AuctionStatus.ACTIVE:
        messages.error(request, f"Auction is {auction_obj.status.value()}")
        return redirect(auction, auction_id)

    # Retrieves and Checks Price
    try:
        price = float(request.POST.get("price"))
    except (TypeError, ValueError):
        messages.error(request, "Price is required and must be number!")
        return redirect(auction, auction_id)

    # Fetches User's Latest Bid On The Auction
    new_bid = Bid.objects.filter(bidder=request.user, auction=auction_obj).first()
    if new_bid:
        new_bid.price = price
    else:
        # Creates New Bid Object
        new_bid = Bid(
            price=price,
            bidder=request.user,
            auction=auction_obj,
        )

    # Saves New Bid and Updates Top_Bid
    if auction_obj.top_bid_handler(new_bid):
        messages.success(request, "Your bid recorded successfully!")
    else:
        messages.error(request, "Something Went Wrong With Your Submission!")
    # returns to auction
    return redirect(auction, auction_id)


# Comment
@login_required
def comment(request, auction_id=None):
    # Check for auction_id argument
    if not auction_id:
        raise Http404("Auction ID is required!")

    # Get's Auction Object Or raises 404 Exception
    auction_obj = get_object_or_404(Auction, id=auction_id)

    # Retrives Submitted Text and Creates Comment
    text = request.POST.get("comment", None)
    if text:
        new_comment = Comment(
            text=text,
            commenter=request.user,
            auction=auction_obj,
        )
        new_comment.save()
        messages.success(request, "You're Comment Submitted Successfully")
    else:
        messages.warning(request, "Comment Did Not Create Duo Lack Of Text!")

    # Redirects
    return redirect(auction, auction_id)


@login_required
def watch_list(request, auction_id=None, action=None):
    """__summary__
    Manage the user's auction watch list.

    Handles adding or removing auctions from the user's watch list based on
    the given `auction_id` and `action`. Requires a POST request.

    Args:
        request (HttpRequest): The HTTP request object.
        auction_id (int): ID of the auction to add/remove.
        action (str): 'add' or 'delete'.

    Raises:
        Http404: For invalid request method, missing parameters, or unknown actions.
    """

    # Initial Error Checking
    if request.method != "POST":
        raise Http404("Only POST request is supported!")
    if not auction_id:
        raise Http404("Auction ID is required!")
    if not action:
        raise Http404("Action is required!")

    # Retrieves Auction Object or Raise an exception
    auction_obj = get_object_or_404(Auction, id=auction_id)

    # Retrieves UserProfile
    profile = getattr(request.user, "userprofile", None)
    if not profile:
        raise Http404("UserProfile Not Found!")

    # Add auction to UserProfile
    if action == "add":
        profile.watch_list.add(auction_obj)
        messages.success(request, f"{auction_obj.name} Added to your watch list!")
        return redirect(auction, auction_id=auction_id)

    # Deletes auction from UserProfile
    elif action == "delete":
        profile.watch_list.remove(auction_obj)
        messages.success(request, f"{auction_obj.name} Deleted From your watch list!")
        return redirect(userprofile)

    # Raises Http404 For Unknown Action
    raise Http404("Action Not Supported!")
