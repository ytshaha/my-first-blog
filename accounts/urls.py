from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static
import django.contrib.auth.views as django_views

from .views import login_page, register_page

app_name='accounts'
urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('logout/', django_views.LogoutView.as_view(next_page='shop/'), name='logout'),


]
