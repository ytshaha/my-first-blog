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
    path('register_ticket/make/', views.make_register_ticket, name='make_register_ticket'),
    path('register_ticket/make/success/', views.make_register_ticket_success, name='make_register_ticket_success'),
    path('register_ticket/send/', views.send_register_ticket, name='send_register_ticket'),
    path('register_ticket/send/success/', views.send_register_ticket_success, name='send_register_ticket_success'),
    path('register_ticket/download/', views.get_register_ticket_excel, name='get_register_ticket_excel'),
    ]


# account/email/confirm/dfa9aakasd -> activation view

