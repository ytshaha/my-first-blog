
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth import views
from django.views.generic import TemplateView, RedirectView

from accounts.views import LoginView, RegisterView, GuestRegisterView, register_success
from django.contrib.auth.views import LogoutView
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
from billing.views import payment_method_view, payment_method_createview
from carts.views import cart_detail_api_view
from shop.views import index, faq, temp

urlpatterns = [
    path('', index, name='home'),

    # 임시 구글인증용
    path('google6d21af56577f529f.html', temp, name='temp'),


    path('admin/', admin.site.urls),
    url(r'^blog/', include('blog.urls')),
    # path('accounts/login/', views.LoginView.as_view(), name='login'),
    # path('accounts/logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    # path('', include('shop.urls')),
    path('login/', LoginView.as_view(), name='login'),
    # path('accounts/login/', RedirectView.as_view(url='/login/')),
    
    url(r'^register/guest/$', GuestRegisterView.as_view(), name='guest_register'),
    url(r'^checkout/address/create/$', checkout_address_create_view, name='checkout_address_create'),
    url(r'^checkout/address/reuse/$', checkout_address_reuse_view, name='checkout_address_reuse'),


    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^register/success/$', register_success, name='register-success'),
    url(r'^billing/payment-method/$', payment_method_view, name='billing-payment-method'),
    url(r'^billing/payment-method/create/$', payment_method_createview, name='billing-payment-method-endpoint'),
    
    # google6d21af56577f529f.html


    path('logout/', LogoutView.as_view(next_page='/product/'), name='logout'),
    path('shop/', include('shop.urls')),
    path('faq/', faq, name='faq'),
    # path('accounts/', include('accounts.urls')),
    url(r'^review/', include('reviews.urls')),
    url(r'^product/', include('products.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^cart/', include('carts.urls')),
    url(r'^order/', include('orders.urls')),
    url(r'^point/', include('points.urls')),
    
    url(r'^account/', include('accounts.urls')),
    url(r'^accounts/', include('accounts.passwords.urls')),
    
    url(r'^ticket/', include('tickets.urls')),
    url(r'^staff/', include('staff.urls')),
    url(r'^api/cart/$', cart_detail_api_view, name='api-cart'),   
    


]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    