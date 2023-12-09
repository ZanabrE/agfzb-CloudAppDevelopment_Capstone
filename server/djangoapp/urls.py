from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL
    #path for to get dealership
    path(route='', view=views.get_dealerships, name='index'),
    #path(route='sample', view=views.sample, name='sample'),
    
    # path for about view
    path(route='about', view=views.about, name='about'),

    # path for contact us view
    path(route='contact', view=views.contact, name='contact'),

    # path for registration
    path(route='registration_request', view=views.registration_request, name='registration_request'),

    # path for login
    path(route='login_request', view=views.login_request, name='login_request'),

    # path for logout
    path(route='logout_request', view=views.logout_request, name='logout_request'),

    # path for dealer reviews view
    path(route='get_dealer_details/<int:id>', view=views.get_dealer_details, name='get_dealer_details'),

    # path for add a review view
    path(route='add_review/<int:id>', view=views.add_review, name='add_review')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)