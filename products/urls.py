from django.urls import path
import django.contrib.auth.views as django_views
from django.conf import settings
from django.conf.urls import url


from django.conf.urls.static import static
from . import views

app_name = 'products'
urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('featured/', views.ProductFeaturedListView.as_view(), name='product_featured_list'), ##
    path('category/<category>/', views.ProductCategoryListView.as_view(), name='product_category_list'), ##
    
    url(r'^detail/<int:pk>/$', views.ProductDetailView.as_view(), name='product_detail'),
    url(r'^detail/(?P<slug>[\w-]+)/$', views.ProductDetailSlugView.as_view(), name='product_detail_slug'),

    path('detail/featured/<int:pk>/', views.ProductFeaturedDetailView.as_view(), name='product_featured_detail'), ##

    # path('<option>/', views.ProductListView.as_view(), name='product_list'),
    # path('upload/', views.product_upload, name='product_upload'),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    