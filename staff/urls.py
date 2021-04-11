from django.urls import path
from . import views

app_name = 'staff'
urlpatterns = [
    path('', views.staff_home, name='home'),
    path('upload/product/', views.UploadProductView.as_view(), name='upload_product'),
    path('upload/product-item/', views.UploadProductItemView.as_view(), name='upload_product_item'),
    path('upload/product/file/', views.upload_product_by_file, name='upload_product_by_file'),
    path('upload/product-item/file/', views.upload_product_item_by_file, name='upload_product_item_by_file'),
    path('upload/product/complete/', views.upload_product_complete, name='upload_product_complete'),
    path('upload/product-item/complete/', views.upload_product_item_complete, name='upload_product_item_complete'),
    path('check/order/', views.StaffOrderCheckListView.as_view(), name='staff_order_check_list'),
    path('check/order/edit/<pk>/', views.StaffOrderEditView.as_view(), name='staff_order_edit'),

    path('product/list/', views.StaffProductListView.as_view(), name='staff_product_list'),
    path('product/edit/<pk>/', views.StaffProductEditView.as_view(), name='staff_product_edit'),
    path('product-item/normal/list/', views.StaffProductItemNormalListView.as_view(), name='staff_product_item_normal_list'),
    path('product-item/normal/edit/<pk>/', views.StaffProductItemNormalEditView.as_view(), name='staff_product_item_normal_edit'),
    path('product-item/normal/option-amount/edit/<pk>/', views.staff_product_item_option_amount_edit, name='staff_product_item_option_amount_edit'),
    path('product-item/bidding/list/', views.StaffProductItemBiddingListView.as_view(), name='staff_product_item_bidding_list'),
    path('product-item/bidding/edit/<pk>/', views.StaffProductItemBiddingEditView.as_view(), name='staff_product_item_bidding_edit'),
]