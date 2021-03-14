from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'points'
urlpatterns = [
    path('', views.PointListView.as_view(), name='home'),
]