from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static

from .views import login_page, register_page

urlpatterns = [
    url(r'^login/$', login_page),
    url(r'^register/$', register_page),

]
