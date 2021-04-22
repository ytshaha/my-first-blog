
from django.shortcuts import render
from django.views import generic
from products.models import ProductItem, Brand, Category
from wishlist.models import Wish
CATEGORY_CHOICES = (
    ('woman', '여성의류'),
    ('man', '남성의류'),
    ('shoes', '신발'),
    ('bag', '가방'),
    ('acc', '명품잡화'),
    ('kid', '키즈'),
)
class SearchProductListView(generic.ListView):
    template_name = 'search/view.html'
    context_object_name = 'product_items'
    
    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductListView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        brands = Brand.objects.all()
        # SearchQuery.objects.create(query=query)
        context['brands'] = brands
        context['is_staff_check'] = False
        
        user = self.request.user
        wish_list = Wish.objects.filter(user=user).values_list('product_item', flat=True)
        context['wish_list'] = wish_list

        context['category_qs'] = CATEGORY_CHOICES
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        print(request.GET)
        query = request.GET.get('q')
        if query is not None:
            return ProductItem.objects.search(query).filter(featured=True).exclude(bidding_on='bidding_end')
        return ProductItem.objects.none()

    