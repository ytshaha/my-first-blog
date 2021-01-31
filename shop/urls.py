from django.urls import path
from . import views
import django.contrib.auth.views as django_views


urlpatterns = [
    path('', views.index, name='index'),
    path('moum/', views.introduction, name='introduction'),
    
    path('product/', views.product_list, name='product_list'),
    path('product/<option>/', views.product_list, name='product_list'),
    path('product/search/', views.product_search, name='product_search'),
    path('upload/', views.product_upload, name='product_upload'),

    path('product/detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/bidding/<int:pk>/', views.bidding, name='bidding'),
    # path('ticket/', views.buying_ticket, name='buying_ticket'),
    path('ticket/', views.buying_ticket, name='buying_ticket'),
    
    path('ticket/result/<int:pk>', views.BuyingTicketResultView.as_view(), name='buying_ticket_result'),
    # path('shop_login/', django_views.LoginView.as_view(), name='shop_login'),
    path('accounts/logout/', django_views.LogoutView.as_view(next_page='/'), name='logout'),
    
]