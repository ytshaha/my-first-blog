from django.urls import path
from . import views
import django.contrib.auth.views as django_views


urlpatterns = [
    path('', views.index, name='index'),
    path('moum/', views.introduction, name='introduction'),
    
    # path('ticket/', views.buying_ticket, name='buying_ticket'),
    path('ticket/', views.buying_ticket, name='buying_ticket'),
    
    path('ticket/result/<int:pk>', views.BuyingTicketResultView.as_view(), name='buying_ticket_result'),
    # path('shop_login/', django_views.LoginView.as_view(), name='shop_login'),
    path('accounts/logout/', django_views.LogoutView.as_view(next_page='/'), name='logout'),
    
]