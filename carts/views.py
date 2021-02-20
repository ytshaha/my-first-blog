from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order
from .models import Cart
from products.models import Product

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0")

stripe.api_key = STRIPE_SECRET_KEY


def cart_detail_api_view(request):
    cart_obj, new_obj, is_cart = Cart.objects.new_or_get(request)
    products = [{
            "id": x.id,
            "url": x.get_absolute_url(),
            "name": x.name, 
            "price":x.start_price,
            } for x in cart_obj.products.all()] # [<object>, <object>, <object>] 그래서 제이슨 형태로 건내줘야힘.
    cart_data = {"products":products, "subtotal":cart_obj.subtotal, "total":cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {'cart':cart_obj})


def cart_update(request):
    product_id = request.POST.get('product_id')
    print(product_id)
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user, product is gone?")
            return redirect("carts:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            # cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session['cart_items'] = cart_obj.products.count()
        if request.is_ajax(): # Asyncronous JavaScripts ANd XM
            print("Ajax request")
            json_data = {
                "added": added,
                'removed':not added,
                "cartItemCount": cart_obj.products.count()
            }
            return JsonResponse(json_data, status=200)
            # return JsonResponse({"message":"Error 400"}, status_code=400) # django rest framework

    return redirect("carts:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("carts:home")   
    
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)
    print("shipping_address_id", shipping_address_id )
    print("billing_address_id", billing_address_id )
    
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    request.session['is_ticket'] = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            print("shipping_address : OK")
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id) 
            del request.session['shipping_address_id']
        if billing_address_id:
            print("billing_address : OK")
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card
    
    # 물건들의 재고가 남아있는지 check
    # order_obj = request.POST.get('order_obj')
    for product in cart_obj.products.all():
        print("Stock Check...product.title")
        if product.amount_always_on < 1:
            print('{}의 재고가 없어 카트에서 제거합니다.'.format(protuct.title))
            cart_obj.products.item.delete()
            print("cart_obj.products: ",cart_obj.products)
            cart_obj.save()
            # 카트에 뭐가있는지 체크아웃도 다시한번하게하기위해 redirect
            return redirect("carts:home")
    

    if request.method == "POST":
        "check that order is done"
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, charge_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                # 재고 있는것들에 대해서 아래와 같이 구매한다.
                for product in cart_obj.products.all():
                    print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(product.title, product.amount_always_on))
                    product.amount_always_on = product.amount_always_on - 1
                    product.save()
                return redirect("carts:success")
            else:
                print(charge_msg)
                return redirect("carts:checkout")

    context = {
        'object':order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        'has_card': has_card,
        'publish_key': STRIPE_PUB_KEY
    }
    return render(request, "carts/checkout.html", context)

def checkout_done_view(request):
    '''
     여기에 product 수량감소시키는 스크립트 작성.
    0보다 높으면 결재가 진행되었다. 깔끔. 수량 감소시키자. 
    bidding여부 field를 추가하여 bidding 이면 그냥 amount. 아니면 amount_always_on을 감소시키자.
    만약 감소시키기 전에 1 보다 낮으면 실패이므로 결재가 진행되지 않았습니다 문구 발생
    그리고 order 는 실패상태로 놔두든가 order에 석세스 실패 여부 field추가하자.
    지금은 일단 일반 prduct만 한정해서 하자.
    나중에 메모장에 적어둔 cart_item 모델을 따로 만들어서 product_always_on, product_bidding, ticket이라고 따로 카테고리화하면 완성 시키자. 
    '''
    # order_obj = request.POST.get('order_obj')
    # for item in order_obj.cart.products.all:
    #     print(item)
    #     if product.amount_always_on < 1:
    #         print('{}의 재고가 없습니다.')
    #     product.amount_always_on = 
    


    return render(request, "carts/checkout-done.html", {})