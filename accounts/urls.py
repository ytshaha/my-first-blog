from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.AccountHomeView.as_view(), name='home'),

    ]


