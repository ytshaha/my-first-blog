from django.urls import path
from . import views
import django.contrib.auth.views as django_views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/bidding/', views.bidding, name='bidding'),
    path('ticket/', views.buying_ticket, name='buying_ticket'),
    path('ticket/result/<int:pk>', views.buying_ticket_result, name='buying_ticket_result'),
    path('accounts/login/', django_views.LoginView.as_view(), name='shop_login'),
    path('accounts/logout/', django_views.LogoutView.as_view(next_page='/'), name='logout'),
    
]