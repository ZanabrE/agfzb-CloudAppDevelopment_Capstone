import requests
import json
# import related models here
from .models import CarDealer
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs): 
    try: 
        response = requests.post(url, params=kwargs, json=json_payload)
        # status_code = response.status_code
        # console.log("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        # console.log(json_data)
        return json_data

    except Exception as e:
        # console.log("Network exception occurred")
        # console.log(e)
        return "error in sentiment analyze"

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Method addition to manage the json depending on what comes back
def get_dealer_by_id_from_cf(url, **kwargs):
    dealer_id = kwargs.get("dealer_id")
    # api_key = kwargs.get("api_key")
    json_result = get_request(url, dealer_id=dealer_id)
    return json_result['docs'][0]

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    dealer_id=kwargs.get("dealer_id")
    api_key = kwargs.get("api_key")

    if dealer_id:
        json_result = get_request(url, dealer_id=dealer_id, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
    else:
        json_result = get_request(url)

    if json_result:
        reviews = json_result["data"]["docs"]

        # For each dealer object
        for dealer_review in reviews:
            review_results = DealerReview(dealership=dealer_review["dealership"],
                                    name=dealer_review["name"],
                                    purchase=dealer_review["purchase"],
                                    review=dealer_review["review"],
                                    # sentiment= dealer_review["sentiment"]
                                   )

            if "id" in dealer_review:
                review_results.id = dealer_review["id"]
            if "purchase_date" in dealer_review:
                review_results.purchase_date = dealer_review["purchase_date"]
            if "car_make" in dealer_review:
                review_results.car_make = dealer_review["car_make"]
            if "car_model" in dealer_review:
                review_results.car_model = dealer_review["car_model"]
            if "car_year" in dealer_review:
                review_results.car_year = dealer_review["car_year"]
            results.append(review_results)
            sentiment = analyze_review_sentiments(review_results.review)
            # print(sentiment)
            review_results.sentiment = sentiment

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerReview, language="en"):
    try:
        url = REVIEW_SENTIMENTS_URL
        api_key = API_KEY
        authenticator = IAMAuthenticator(api_key)
        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
        natural_language_understanding.set_service_url(url)
        response = natural_language_understanding.analyze( text=dealerReview+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[dealerReview+"hello hello hello"]))).get_result()
        label=json.dumps(response, indent=2)
        label = response['sentiment']['document']['label']
        return(label)
    except(requests.exceptions.RequestException, ConnectionResetError) as err:
        print("connection error")
        return {"error": err}
