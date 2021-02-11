
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth import views
from accounts.views import login_page, register_page, guest_register_view
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/login/', views.LoginView.as_view(), name='login'),
    # path('accounts/logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    # path('', include('shop.urls')),
    path('login/', login_page, name='login'),
    path('register/guest/', guest_register_view, name='guest_register'),
    
    path('register/', register_page, name='register'),
    path('logout/', LogoutView.as_view(next_page='product/'), name='logout'),
    path('shop/', include('shop.urls')),
    # path('accounts/', include('accounts.urls')),
    url(r'^product/', include('products.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^cart/', include('carts.urls')),   
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    