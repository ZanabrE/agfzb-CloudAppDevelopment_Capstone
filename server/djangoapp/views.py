from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, CarMake, CarModel
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .restapis import *
import logging
import json


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
#def sample(request):
    #render function takes argument  - request 
    #and return HTML as response 
    #return render(request, "sample.html")

# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        context = {}
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        context = {}
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp/index.html')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to index page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        #url = "https://us-south.functions.appdomain.cloud/api/v1/web/ddcdeeb5-bec2-481e-b506-af4fdbb68aa7/dealership-package/get-dealership"
        #dealerships = get_dealers_from_cf(url)
        #context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        reviews_url = REVIEWS_URL
        dealers_url = DEALERS_URL
        #Get the reviews
        review_results = get_dealer_reviews_from_cf(reviews_url, dealer_id=id, api_key=API_KEY)
        # get the details about the dealer itself
        dealer_result = get_dealer_by_id_from_cf(dealers_url, dealer_id=id, api_key=API_KEY)

        context['dealer'] = dealer_result
        context['reviews'] = review_results
        # console.log(context['reviews'])
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, id):

    # Prep and render the page we will need to post a review
    if request.method == 'GET':
        context = {}
        dealer_url = DEALER_BY_ID_URL
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=id)
        context["dealer"] = dealer

        # Get cars for the dealer
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    
    elif request.method == 'POST':
        if request.user.is_authenticated:

            username = request.user.username

            
            payload = dict() # Set up empty dictionary for the post

            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)

            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["id"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchase_date"]
            payload["car_make"] = car.make.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year)

            new_payload = {}
            new_payload["review"] = payload

            review_post_url = REVIEWS_POST_URL
            post_request(review_post_url, new_payload, id=id, api_key=API_KEY)
        return redirect("djangoapp:get_dealer_details", id=id)
