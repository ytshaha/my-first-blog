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
    

]