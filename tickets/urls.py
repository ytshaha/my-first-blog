from django.urls import path
from django.conf import settings
from django.conf.urls import url

from django.conf.urls.static import static
from . import views

app_name = 'tickets'
urlpatterns = [
    path('', views.ticket_home, name='home'),
    # path('list/', views.TicketAvailableListView, name='list'),
    path('buy/', views.ticket_buy, name='buy'),
    path('cart/', views.ticket_cart_home, name='cart'),
    path('checkout/', views.ticket_checkout_home, name='checkout'),
    url(r'^checkout/success/$', views.checkout_done_view, name='success'),



    ]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    