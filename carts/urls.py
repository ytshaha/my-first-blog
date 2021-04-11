from django.urls import path
import django.contrib.auth.views as django_views
from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView


from django.conf.urls.static import static
from . import views

app_name = 'carts'
urlpatterns = [
    path('', views.cart_home, name='home'),
    url(r'^update/$', views.cart_update, name='update'),
    # url(r'^checkout/$', views.checkout_home, name='checkout'),
    url(r'^checkout/success/$', views.checkout_done_view, name='success'),
    url(r'^checkout/fail/$', views.checkout_fail_view, name='fail'),
    url(r'^checkout/vbank/$', views.checkout_vbank_view, name='vbank'),
    
    # 테스트중.
    url(r'^checkout/iamport/$', views.checkout_iamport, name='checkout-iamport'),

    url(r'^payment/test/$', TemplateView.as_view(template_name='carts/payment_test.html'), name='payment_test'),
    url(r'^payment/complete/$', views.payment_complete, name='payment_complete'),
    url(r'^payment/fail/$', views.payment_fail, name='payment_fail'),
    url(r'^payment/success/$', views.payment_success, name='payment_success'),
    ]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        