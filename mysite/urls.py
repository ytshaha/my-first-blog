
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth import views


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/login/', views.LoginView.as_view(), name='login'),
    # path('accounts/logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    # path('', include('shop.urls')),
    path('shop/', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('product/', include('products.urls')),
    path('search/', include('search.urls')),
    path('cart/', include('carts.urls')),   
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    