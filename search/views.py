from django.shortcuts import render
from django.views import generic
from products.models import Product

class SearchProductListView(generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        print(request.GET)
        query = request.GET.get('q')
        if query is not None:
            return Product.objects.filter(title__icontains=query)   #order_by('-bidding_date')
        return Product.objects.none()