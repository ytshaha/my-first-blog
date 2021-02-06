from django.urls import path
import django.contrib.auth.views as django_views
from django.conf import settings

from django.conf.urls.static import static
from . import views

app_name = 'search'
urlpatterns = [
    path('', views.SearchProductListView.as_view(), name='query'),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    