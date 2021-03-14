from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.shortcuts import render

from .models import Point

# Create your views here.
class PointListView(LoginRequiredMixin, generic.ListView):
    '''
    Featured = True이고 product_type= Noraml인 물품들을 표시함.(active와 다른 개념. active는 구매가능여부.)
    '''
    template_name = 'points/home.html'
    context_object_name = 'points'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super(PointListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        point_qs = Point.objects.filter(user=self.request.user)
        return point_qs.order_by('-timestamp')