from django.urls import path
import django.contrib.auth.views as django_views
from django.conf import settings
from django.conf.urls import url


from django.conf.urls.static import static
from . import views
from biddings.views import bidding_new, bidding_result


app_name = 'products'
urlpatterns = [
    # 일반물품 URL
    path('', views.ProductNormalListView.as_view(), name='product_list'), 
    # path('filter/', views.ProductFilterListView.as_view(), name='product_filter_list'), 
    
    path('category/<category>/', views.ProductNormalListView.as_view(), name='product_list'), 
    path('brand/<brand>/', views.ProductNormalListView.as_view(), name='product_list'), 
    path('wishlist/', views.ProductWishListView.as_view(), name='product_wish_list'), 
    path('wishlist/category/<category>/', views.ProductWishListView.as_view(), name='product_wish_list'), 
    path('wishlist/brand/<brand>/', views.ProductWishListView.as_view(), name='product_wish_list'), 
    # 경매물품 URL
    path('bidding/', views.ProductBiddingListView.as_view(), name='product_bidding_list'), 
    path('bidding/category/<category>/', views.ProductBiddingListView.as_view(), name='product_bidding_list'), 
    path('bidding/brand/<brand>/', views.ProductBiddingListView.as_view(), name='product_bidding_list'), 
    path('bidding/complete/', views.ProductBiddingCompleteListView.as_view(), name='product_bidding_end_list'), 
    
    # 렌탈물품 URL
    path('rental/', views.ProductRentalListView.as_view(), name='product_rental_list'), 
    path('rental/category/<category>/', views.ProductRentalListView.as_view(), name='product_rental_list'), 
    path('rental/brand/<brand>/', views.ProductRentalListView.as_view(), name='product_rental_list'), 
    

    # path('featured/', views.ProductFeaturedListView.as_view(), name='product_featured_list'), #
    path('check/', views.ProductStaffCheckView.as_view(), name='check'), # 스탭이 물품 올리기전 체크
    path('check/make_featured/', views.product_make_featured, name='product_make_featured'), # 스탭이 물품 올리기전 체크
    path('check/make_unfeatured/', views.product_make_unfeatured, name='product_make_unfeatured'), # 스탭이 물품 올리기전 체크
    


    # url(r'^detail/<int:pk>/$', views.ProductDetailView.as_view(), name='product_detail'),
    url(r'^detail/(?P<slug>[\w-]+)/$', views.ProductDetailSlugView.as_view(), name='product_detail'),
    url(r'^bidding/detail/(?P<slug>[\w-]+)/$', views.ProductDetailSlugView.as_view(), name='product_bidding_detail'),
    url(r'^detail/(?P<slug>[\w-]+)/bidding/$', bidding_new, name='bidding_new'),
    url(r'^detail/(?P<slug>[\w-]+)/result/$', bidding_result, name='bidding_result'),

    # path('<option>/', views.ProductListView.as_view(), name='product_list'),
    path('upload/product/', views.upload_product, name='upload_product'),
    path('upload/product-item/', views.UploadProductItemView.as_view(), name='upload_product_item'),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
