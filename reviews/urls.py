from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'reviews'
urlpatterns = [
    path('', views.ReviewListView.as_view(), name='home'),
    path('upload/', views.ReviewUploadView.as_view(), name='upload'),
    path('detail/<pk>/', views.ReviewDetailView.as_view(), name='detail'),
    path('detail/<pk>/edit/', views.ReviewEditView.as_view(), name='edit'),
    
    path('commnet/<pk>/add/', views.add_comment_to_review, name='add_comment_to_review'),
    path('comment/<pk>/remove/', views.CommentRemoveView.as_view(), name='comment_remove'),
    path('comment/<pk>/edit/', views.CommentEditView.as_view(), name='comment_edit'),
    
    ]
