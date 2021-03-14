from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.AccountHomeView.as_view(), name='home'),
    path('details/', views.UserDetailUpdateView.as_view(), name='user-update'),
    # url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/%', views.AccountEmailActivateView.as_view(), name='email-activate'),
    path('email/confirm/<key>/', views.AccountEmailActivateView.as_view(), name='email-activate'),
    path('email/resend-activation/', views.AccountEmailActivateView.as_view(), name='resend-activation'),
    ]


# account/email/confirm/dfa9aakasd -> activation view

