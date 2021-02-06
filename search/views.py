
from django.shortcuts import render
from django.views import generic
from products.models import Product

class SearchProductListView(generic.ListView):
    template_name = 'search/view.html'
    context_object_name = 'products'
    
    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductListView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        # SearchQuery.objects.create(query=query)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        print(request.GET)
        query = request.GET.get('q')
        if query is not None:
            return Product.objects.search(query)
        return Product.objects.none()