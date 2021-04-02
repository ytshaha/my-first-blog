from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
import json

from .models import Wish
from products.models import ProductItem
# Create your views here.


def make_wishlist(request):
    # if request.method == 'POST':
    #     user = request.user
    #     product_item = request.POST.get('product_item')
    #     print(product_item)
    #     product_item_obj = ProductItem.objects.get(slug=product_item)
    #     wish_obj = Wish.objects.create(user=user, product_item=product_item_obj)
    #     next_url = request.POST.get('next', '/')
    #     return redirect(next_url)
    if request.method == 'POST' and request.is_ajax():
        user = request.user
        product_item = request.POST.get('product_item')
        product_item_obj = ProductItem.objects.get(slug=product_item)
        wish_qs = Wish.objects.filter(user=user, product_item=product_item_obj)
        if wish_qs.count() > 0:
            wish_qs.delete()
            print("싹다 지웁니다.")
            return HttpResponse(json.dumps({'status': "success", 'added': "false"}),
                                    content_type="application/json")
        elif wish_qs.count() == 0:
            wish_obj = Wish.objects.create(user=user, product_item=product_item_obj)
            print("만듭니다.")
            return HttpResponse(json.dumps({'status': "success", 'added': "true"}),
                            content_type="application/json")

        # next_url = request.POST.get('next', '/')
    
# def remove_wishlist(request):
#     # if request.method == 'POST':
#     #     user = request.user
#     #     product_item = request.POST.get('product_item')
#     #     product_item_obj = ProductItem.objects.get(slug=product_item)
#     #     wish_qs = Wish.objects.filter(user=user, product_item=product_item_obj)
#     #     wish_qs.delete()
#     #     # if wish_qs.count() == 1:
#     #     #     wish_obj = wish_qs.first()
#     #     #     wish_obj.delete()
#     #     next_url = request.POST.get('next', '/')
#     #     return redirect(next_url)
#     if request.method == 'POST' and request.is_ajax():
#         print("remove_wishlist 호출되써여 if들어오써요")
#         user = request.user
#         product_item = request.POST.get('product_item')
#         product_item_obj = ProductItem.objects.get(slug=product_item)
#         wish_qs = Wish.objects.filter(user=user, product_item=product_item_obj)
#         wish_qs.delete()
#         # next_url = request.POST.get('next', '/')
#         return HttpResponse(json.dumps({'status': "success", 'message': "좋아요제거"}),
#                                     content_type="application/json")