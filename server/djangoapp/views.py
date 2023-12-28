from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
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
    #if request.method == "GET":
        #context = {}
        #render function takes argument  - request 
        #and return HTML as response 
        #return render(request, 'djangoapp/sample.html', context)

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

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Successfully logged in!')
            return redirect("djangoapp:index")
        else:
            messages.add_message(request, messages.ERROR, 'Unable to log in. Please try again.')
            return render(request, 'djangoapp/login.html', {'onLoginPage':True} )
    else:
        return render(request, 'djangoapp/login.html', {'onLoginPage':True} )

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect("djangoapp:index")

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    
    if request.method == 'POST':
        # get the form's data
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        psw = request.POST['psw']
        userExists = False

        # Check if the username exists
        try: 
            User.objects.get(username=username)
            userExists = True
        except Exception as error:
            logger.info(error)
            logger.debug("{} is new user".format(username))

        # Send user feedback that the username is taken
        if userExists:
            messages.add_message(request, messages.ERROR, 'That username is taken, please use a different username.')
            return render(request, 'djangoapp/registration.html', {'firstname': first_name, 'lastname': last_name})
        else:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=psw)
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Succesfully signed in!')
            return redirect("djangoapp:index")


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://ernestozanab-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://ernestozanab-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer
        # print(dealer)
    
        review_url = "https://ernestozanab-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get_reviews"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        # print(reviews)
        context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, id):

    # Prep and render the page we will need to post a review
    if request.method == 'GET':
        context = {}
        dealer_url = "https://ernestozanab-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
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
