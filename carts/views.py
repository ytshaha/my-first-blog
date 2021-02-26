import json
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
import requests

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order
from .models import Cart, CartItem
from biddings.models import Bidding
from products.models import Product
from tickets.models import Ticket
from mysite.utils import random_string_generator

import stripe

STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0")

stripe.api_key = STRIPE_SECRET_KEY

from mysite.client import Iamport

IAMPORT_CODE = getattr(settings, "IAMPORT_CODE", 'imp30832141')
IMPORT_REST_API_KEY = getattr(settings, "IMPORT_REST_API_KEY", '8306112827056798')
IMPORT_REST_API_SECRET = getattr(settings, "IMPORT_REST_API_SECRET", 'WmAHFCAyZFfaMy10g6xRPvFawuuJAVPxiqfY2Pw2uMcgkegAlOsak7kQCOzdKpK2PZ0RPxTjj6AEkQfF')




def select_price(cart_item):
    '''
    cart_detail_api_view에서 JSON 형태로 넘겨줄때 price를 정의해주기 위한 함수.
    bidding이면 current_price를
    normal이면 limit_price를 return
    '''
    product_type = cart_item.product_type
    user = cart_item.user

    if product_type == "bidding":
        return Bidding.objects.get(user=user, product=product_obj, win=True).bidding_price
    elif product_type == "normal":
        return cart_item.product_obj.limit_price
    else:
        return None

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    cart_items = [{
            "id": x.id,
            "url": x.product.get_absolute_url(),
            "name": x.product.name, 
            # "price":x.product.current_price,
            "price":select_price(x),
            "amount":x.amount
            } for x in cart_obj.cart_items.all()] # [<object>, <object>, <object>] 그래서 제이슨 형태로 건내줘야힘.
    cart_data = {"cart_items":cart_items, "subtotal":cart_obj.subtotal, "total":cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {'cart':cart_obj})


def cart_update(request):
    '''
    원래 강의에서는 물품의 갯수도 상관없고 그냥 바로 제거하는 것으로 되어있음.
    카트에서 다시누를때만 remove 되게하고 나머지 위치에서는 무조건 추가만하게 하는것으로 하는게 나을 것 같다.

    2021.02.24 update
    Bidding 물품 갯수는 User당 1개 그대로고 단 상시상품 구매는 재고내 구매 즉 복수로 구매가 가능하다.
    그래서 만약 구매버튼을 누르게 될때 그 amount가 기존 값과 합쳐서 재고보다 높으면 그냥 재고수량을 카트에 넣는걸로 해줘야겠다.
    재고보다 낮으면 기존 cart_item.amount + request.POST.get("amount")로 해주면 되겠다.
    remove 컨셉은 기존과동일하게 cart_home안에서만 가능하다.

    아니다 수량 변경은 못하게 하자..
    그냥 product_detail에서 POST 받아오는 수량이 무조건 그 수량이 되는것이다.
    '''
    print('request.POST',request.POST)
    product_id = request.POST.get('product_id')
    product_type = request.POST.get('product_type')

    # 경매든 그냥 상시상품이든 티켓없으면 티켓사라고 한다.
    user = request.user
    ticket_qs = Ticket.objects.filter(user=user, status='activate')
    if not ticket_qs.exists() and product_type == 'normal':
        messages.success(request, "상시판매 상품을 구매하기 위해서는 티켓이 필요합니다. 티켓을 구매하고 활성화 시키십시오.")
        return redirect("tickets:home")

    # 추가수량에 대해 POST로 오면 업뎃
    # 이부분이 product_type으로 if문을 추가로 안에 넣을지는 고민 필요.
    if product_type == "bidding":
        amount = 1 # 경매상품일때
    elif product_type == "normal":
        amount = request.POST.get('amount') # 상시상품일때
   
    only_add = True
    try:
        if request.POST.get('at_cart'):
            only_add = False
    except:
        pass
    print(only_add)
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user, product is gone?")
            return redirect("carts:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        cart_item_obj, new_item_obj = CartItem.objects.new_or_get(request)
         
        # 1. remove인경우 처리
        if cart_item_obj in cart_obj.cart_items.all() and not only_add:
            cart_obj.cart_items.remove(cart_item_obj)
            added = False
            # 부득이하게 여기에 cart_item계산을 한번 더 넣는다... jquery잘하게 되면 다시 구현하자.
            request.session['cart_items'] = cart_obj.cart_items.count()
            return redirect("carts:home")

        # 2. 그냥 추가 혹은 수량조정인경우
        # m2m Change가 적용되려면 cart_item의 수량과 단가가 확정되어야함.
        
        # 단가확정
        if product_type == 'bidding':
            price = Bidding.objects.get(user=user, product=product_obj, win=True).bidding_price
        elif product_type == 'normal':
            price = product_obj.limit_price
        cart_item_obj.price = price
        cart_item_obj.amount = amount
        cart_item_obj.save()

        if cart_item_obj in cart_obj.cart_items.all() and only_add:
            # m2mchange가 안되서 그냥 지웠다가 다시 추가함.
            cart_obj.cart_items.remove(cart_item_obj)
            cart_obj.cart_items.add(cart_item_obj)
            added = False
        # 처음 추가되는 cart_item일경우
        else:
            cart_obj.cart_items.add(cart_item_obj)
            added = True
            
            
        # 그냥 나중에 쓸수도 있는 json이기에 남겨둠.
        request.session['cart_items'] = cart_obj.cart_items.count()
        if request.is_ajax(): # Asyncronous JavaScripts ANd XM
            print("Ajax request")
            json_data = {
                "added": added,
                'removed':not added,
                "cartItemCount": cart_obj.cart_items.count()
            }
            return JsonResponse(json_data, status=200)
            # return JsonResponse({"message":"Error 400"}, status_code=400) # django rest framework

    return redirect("carts:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.cart_items.count() == 0:
        return redirect("carts:home")   
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
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
    print(150, 'has_card',has_card)
    # 물건들의 재고가 남아있는지 check
    # order_obj = request.POST.get('order_obj')
    stock_refresh = False # 괜찮으면 넘어가고 안괜찮으면 스탁없는 물품들을 refresh하기 위해 carts:home 보냄.
    for cart_item_obj in cart_obj.cart_items.all():
        print("Stock Check...product.title")
        if cart_item_obj.product_type == 'normal':
            if cart_item_obj.product.amount_always_on < 1:
                print('{}의 재고가 없어 카트에서 제거합니다.'.format(cart_item_obj.product.title))
                cart_obj.cart_items.remove(cart_item_obj)
                cart_obj.save()
                stock_refresh = True
        elif cart_item_obj.product_type == 'bidding':
            pass
    if stock_refresh:
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
                for cart_item_obj in cart_obj.cart_items.all():
                    if cart_item_obj.product_type == 'normal':
                        cart_item_obj.product.amount_always_on = cart_item_obj.product.amount_always_on - 1
                        cart_item_obj.product.save()
                        print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product.title, cart_item_obj.product.amount_always_on))
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
    print('♥♥♥♥♥context')
    print(context)
    
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


#############아임포트로 체크아웃 재구현###################


def checkout_iamport(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.cart_items.count() == 0:
        return redirect("carts:home")   
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
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
    stock_refresh = False # 괜찮으면 넘어가고 안괜찮으면 스탁없는 물품들을 refresh하기 위해 carts:home 보냄.
    for cart_item_obj in cart_obj.cart_items.all():
        print("Stock Check...product.title")
        if cart_item_obj.product_type == 'normal':
            if cart_item_obj.product.amount_always_on < 1:
                print('{}의 재고가 없어 카트에서 제거합니다.'.format(cart_item_obj.product.title))
                cart_obj.cart_items.remove(cart_item_obj)
                cart_obj.save()
                stock_refresh = True
        elif cart_item_obj.product_type == 'bidding':
            pass
    if stock_refresh:
        return redirect("carts:home")

    # ################################################################
    # ################################################################
    # ################################################################
    # ################################################################
    
    # 아임포트 토큰 가져오기
    iamport = Iamport(imp_key=IMPORT_REST_API_KEY, imp_secret=IMPORT_REST_API_SECRET)
    # access_token = iamport._get_token()
    # response = iamport.get_response(access_token)
    # 결재정보 받아오기위한 json data 준비
    user = request.user

    shipping_address_qs = Address.objects.filter(billing_profile__email=user.email, address_type='shipping')
    if shipping_address_qs.count() == 1:
        shipping_address_obj = shipping_address_qs.first()
    else:
        print('address에 문제가 있다.')
    address = shipping_address_obj.get_address()
    postcode = shipping_address_obj.get_postal_code()
    
    cart_items_name = ""
    for cart_item in cart_obj.cart_items.all():
        cart_items_name = cart_items_name + cart_item.product.title + "_"
    print('cart_items_name',cart_items_name)
    print("request.POST", request.POST)
    iamport_data = {
                'pg': "html5_inicis",
                'pay_method':'card',
                'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
                'name':cart_items_name,
                'amount': int(order_obj.total),
                'buyer_email': billing_profile.email,
                'buyer_name': user.full_name,
                'buyer_tel': user.phone_number,# 얘는 만들어야함. 
                'buyer_addr': address,
                'buyer_postcode': postcode
                }
    if request.method == 'POST' and request.is_ajax():
        get_data = request.POST.get('get_data')
        print(380, "get_data",get_data)
        # if not get_data:
        #     # imaport_data 가져오기 버튼 누름.
        #     return JsonResponse(iamport_data)
        # else:
        #     print(385, ' elif not get_data',get_data)
        # 결재정보 확인 실행
        imp_uid = request.POST.get('imp_uid')
        # // 액세스 토큰(access token) 발급받기
        data = {
            "imp_key": IMPORT_REST_API_KEY,
            "imp_secret": IMPORT_REST_API_SECRET
        }
        print(data)
        response = requests.post('https://api.iamport.kr/users/getToken', data=data)
        data = response.json()
        print(data)
        my_token = data['response']['access_token']
        print('my_token',my_token)
        #  // imp_uid로 아임포트 서버에서 결제 정보 조회
        headers = {"Authorization": my_token}
        response = requests.get('https://api.iamport.kr/payments/'+imp_uid, data=data, headers = headers)
        data = response.json()
        # // DB에서 결제되어야 하는 금액 조회 const
        order_amount = order_obj.total
        amountToBePaid = data['response']['amount']  # 아임포트에서 결제후 실제 결제라고 인지 된 금액
        print('amountToBePaid',amountToBePaid)
        status = data['response']['status']  # 아임포트에서의 상태
        print('status',status)
        if order_amount==amountToBePaid:
            # DB에 결제 정보 저장
            # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
            if status == 'ready':
                # DB에 가상계좌 발급정보 저장
                print("결재 상태 : ready, vbankIssued")
                return HttpResponse(json.dumps({'status': "vbankIssued", 'message': "가상계좌 발급 성공"}),
                                    content_type="application/json")
            elif status=='paid':
                print("결재 상태 : paid, success")

                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                # 재고 있는것들에 대해서 아래와 같이 구매한다.
                for cart_item_obj in cart_obj.cart_items.all():
                    if cart_item_obj.product_type == 'normal':
                        cart_item_obj.product.amount_always_on = cart_item_obj.product.amount_always_on - 1
                        cart_item_obj.product.save()
                        print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product.title, cart_item_obj.product.amount_always_on))



                return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
                                    content_type="application/json")
            else:
                pass
        else:
            print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
            return HttpResponse(json.dumps({'status': "forgery", 'message': "위조된 결제시도"}), content_type="application/json")
        

    context = {
        'object':order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        'has_card': has_card,
        'publish_key': STRIPE_PUB_KEY,
        # 결재용 context
        'pg': "html5_inicis",
        'pay_method':'card',
        'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
        'name':cart_items_name,
        'amount': order_obj.total,
        'buyer_email': billing_profile.email,
        'buyer_name': user.full_name,
        'buyer_tel': user.phone_number,# 얘는 만들어야함. 
        'buyer_addr': address,
        'buyer_postcode': postcode
        # 'pg' : 'html5_inicis', 
        # 'pay_method' : 'card',
        # 'merchant_uid' : 'merchant_' + random_string_generator(size=10),
        # 'name' : '주문명:결제테스트',
        # 'amount' : 100,
        # 'buyer_email' : 'iamport@siot.do',
        # 'buyer_name' : '고길동',
        # 'buyer_tel' : '010-1234-5678',
        # 'buyer_addr' : '서울특별시 영등포구 도신로',
        # 'buyer_postcode' : '123-456',

                }
    
    # print('♥♥♥♥♥context')
    # print(context)
    
    return render(request, "carts/checkout-iamport.html", context)

    

class CheckoutView(generic.TemplateView):
    template_name='carts/payment_test.html'
    

# @csrf_exempt

def payment_complete(request):
    print('request', request)
    print('request.POST', request.POST)
    if request.method == 'POST' and request.is_ajax():
        imp_uid = request.POST.get('imp_uid')
        # // 액세스 토큰(access token) 발급받기
        data = {
            "imp_key": IMPORT_REST_API_KEY,
            "imp_secret": IMPORT_REST_API_SECRET
        }
        response = requests.post('https://api.iamport.kr/users/getToken', data=data)
        data = response.json()
        my_token = data['response']['access_token']
        print('my_token',my_token)
        #  // imp_uid로 아임포트 서버에서 결제 정보 조회
        headers = {"Authorization": my_token}
        response = requests.get('https://api.iamport.kr/payments/'+imp_uid, data=data, headers = headers)
        data = response.json()
        # // DB에서 결제되어야 하는 금액 조회 const
        order_amount = 100
        amountToBePaid = data['response']['amount']  # 아임포트에서 결제후 실제 결제라고 인지 된 금액
        print('amountToBePaid',amountToBePaid)
        status = data['response']['status']  # 아임포트에서의 상태
        print('status',status)
        if order_amount==amountToBePaid:
            # DB에 결제 정보 저장
            # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
            if status == 'ready':
                # DB에 가상계좌 발급정보 저장
                print("결재 상태 : ready, vbankIssued")
                return HttpResponse(json.dumps({'status': "vbankIssued", 'message': "가상계좌 발급 성공"}),
                                    content_type="application/json")
            elif status=='paid':
                print("결재 상태 : paid, success")
                return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
                                    content_type="application/json")
            else:
                pass
        else:
            print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
            return HttpResponse(json.dumps({'status': "forgery", 'message': "위조된 결제시도"}), content_type="application/json")
    else:
        print("Not post or Not Ajax requested.")
        return render(request, 'carts/payment_complete.html')   #수정 필요

def payment_fail(request):
    return render(request, 'carts/payment_fail.html', {})

def payment_success(request):
    return render(request, 'carts/payment_success.html', {})