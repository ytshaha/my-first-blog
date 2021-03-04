from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'reviews'
urlpatterns = [
    path('', views.ReviewListView.as_view(), name='home'),
    path('upload/', views.ReviewUploadView.as_view(), name='upload'),
    path('detail/<pk>/', views.ReviewDetailView.as_view(), name='detail'),
    ]
