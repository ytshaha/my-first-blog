from django.urls import path
from django.conf import settings
from django.conf.urls import url

from django.conf.urls.static import static
from . import views

app_name = 'wishlist'
urlpatterns = [
    path('make_wish/', views.make_wishlist, name='make_wishlist'),
    path('remove_wish/', views.remove_wishlist, name='remove_wishlist'),


    # make_wishlist
]