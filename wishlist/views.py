from django.shortcuts import render, get_object_or_404, redirect
from .models import Wish
from products.models import ProductItem
# Create your views here.


def make_wishlist(request):
    if request.method == 'POST':
        user = request.user
        product_item = request.POST.get('product_item')
        print(product_item)
        product_item_obj = ProductItem.objects.get(slug=product_item)
        wish_obj = Wish.objects.create(user=user, product_item=product_item_obj)
        next_url = request.POST.get('next', '/')
        return redirect(next_url)
    
def remove_wishlist(request):
    if request.method == 'POST':
        user = request.user
        product_item = request.POST.get('product_item')
        product_item_obj = ProductItem.objects.get(slug=product_item)
        wish_obj = Wish.objects.get(user=user, product_item=product_item_obj)
        wish_obj.delete()
        next_url = request.POST.get('next', '/')
        return redirect(next_url)
    