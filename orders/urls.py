from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<order_id>/', views.OrderDetailView.as_view(), name='detail'),
    path('order/cancel/cancel/', views.cancel_order, name='cancel_order'),
    path('order/cancel/', views.cancel_request, name='cancel_request'),
    path('order/rental/', views.RentalListView.as_view(), name='rental_list'),
    path('order/rental/cancel/', views.cancel_rental, name='cancel_rental'),

    ]
