from django.urls import path
import django.contrib.auth.views as django_views
from django.conf import settings

from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('featured/', views.ProductFeaturedListView.as_view(), name='product_featured_list'), ##
    path('detail/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('detail/<str:slug>/', views.ProductDetailSlugView.as_view(), name='product_detail'),

    path('detail/featured/<int:pk>/', views.ProductFeaturedDetailView.as_view(), name='product_featured_detail'), ##

    path('<option>/', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path('upload/', views.product_upload, name='product_upload'),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    