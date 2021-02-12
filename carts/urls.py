from django.urls import path
import django.contrib.auth.views as django_views
from django.conf import settings
from django.conf.urls import url

from django.conf.urls.static import static
from . import views

app_name = 'carts'
urlpatterns = [
    path('', views.cart_home, name='home'),
    url(r'^update/$', views.cart_update, name='update'),
    url(r'^checkout/$', views.checkout_home, name='checkout'),
    url(r'^checkout/success/$', views.checkout_done_view, name='success'),
    ]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    