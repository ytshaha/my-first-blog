import requests
import json
import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.template.loader import get_template

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import requests

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address

from billing.models import BillingProfile, Charge, Card
from orders.models import Order, OrderAddress
from .models import Cart, CartItem
from biddings.models import Bidding
from products.models import Product, ProductItem, SizeOption
from tickets.models import Ticket, TicketItem
from points.models import Point
from mysite.utils import random_string_generator
from mysite.alimtalk import send
# import stripe

# STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
# STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0")

# stripe.api_key = STRIPE_SECRET_KEY

from mysite.client import Iamport

IAMPORT_CODE = getattr(settings, "IAMPORT_CODE", 'imp30832141')
IMPORT_REST_API_KEY = getattr(settings, "IMPORT_REST_API_KEY", '8306112827056798')
IMPORT_REST_API_SECRET = getattr(settings, "IMPORT_REST_API_SECRET", 'WmAHFCAyZFfaMy10g6xRPvFawuuJAVPxiqfY2Pw2uMcgkegAlOsak7kQCOzdKpK2PZ0RPxTjj6AEkQfF')

POSTAL_CODE_INFORMATION_DIRS = getattr(settings, "POSTAL_CODE_INFORMATION_DIRS", None)


def select_price(cart_item):
    '''
    cart_detail_api_view에서 JSON 형태로 넘겨줄때 price를 정의해주기 위한 함수.
    bidding이면 current_price를
    normal이면 limit_price를 return
    ticket이면 TicketItem.total
    '''
    product_type = cart_item.product_type
    user = cart_item.user

    if product_type == "bidding":
        return Bidding.objects.get(user=user, product_item=cart_item.product_item, win=True).bidding_price
    elif product_type == "normal":
        return cart_item.product_item_obj.price
    elif product_type == "ticket":
        return cart_item.ticket_item.total

@login_required
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

@login_required
def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    if request.method == 'POST':
        post_purpose = request.POST.get('post_purpose', None)
        cart_item_id = request.POST.get('cart_item_id', None)
        add = request.POST.get('add', None)
        
        if post_purpose == 'add_certificate':
            cart_item_qs = CartItem.objects.filter(id=cart_item_id)
            
            cart_item_obj = cart_item_qs.first()
            if add == 'True':
                print("추가되는거 실행")
                cart_item_obj.add_certificate = True
                cart_item_obj.save()

                cart_items = cart_obj.cart_items.all()
                total = 0
                for x in cart_items: # x는 개별 cart_items
                    total += x.total
                cart_obj.total = total
                cart_obj.subtotal = total
                
                cart_obj.save()
                print('cart_obj.total',cart_obj.total)

            elif add == 'False':
                print("제거되는거 실행")
                cart_item_obj.add_certificate = False
                cart_item_obj.save()

                cart_items = cart_obj.cart_items.all()
                total = 0
                for x in cart_items: # x는 개별 cart_items
                    total += x.total
                cart_obj.total = total
                cart_obj.subtotal = total
                
                cart_obj.save()
                print('cart_obj.total',cart_obj.total)


    print('카트홈에 있는 cart_obj',cart_obj, cart_obj.total, cart_obj.subtotal)
    return render(request, "carts/home.html", {'cart':cart_obj})


# def select_purchase_way(request):
#     print('★★★★★★★리퀘스트 포스트 프린트')
#     print(request.POST)
#     if request.method == 'POST':
#         product_item_id = request.POST.get('product_item_id', None)
#         product_item_obj = ProductItem.objects.get(id=product_item_id)
#         action = request.POST.get('action', None)
#         if action == '장바구니 담기':
#             print("장바구니 담기 실행")
#             cart_update(request)
#             return redirect('carts:home')
#         elif action == '바로구매':
#             print("바로구매 실행")
#             checkout_iamport_now(request)
#             return redirect('carts:checkout_iamport_now')
#     else:
#         pass
#     return redirect('products:product_detail', slug=product_item_obj.slug)


@login_required
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
    2021.03.03 update
    티켓도 여기 카트에서 구매가능하게 업뎃하자.

    2021.03.04 update
    cart update엔 3가지의 POST가 있다.
    1. 티켓구매에서 오는거
    2. 물품구매에서 오는거
    3. 카트의 remove칸에서 오는거

    각각의 POST는 아래와 같다. 
    1. 티켓구매 : ticket_item_id, product_type
    2. 물품구매 : product_item_id, product_type
    3. 카트의 remove : cart_item_id, product_type, at_cart
    
    at_cart로 일단 remove가 구현이 안되어있다. 해당 parameter로 구분해서 그 케이스를 구현하자.

    2021.04.03 update
    늦게나마 업데이트 한다. 
    같은 물품 다른 사이즈 구매시 카트에 추가되게하자

    cart_item이 경우에 따라 추가 혹은 그냥 get하게 한다.

    1. normal 
    - option 없으면 그냥 현재와 동일하게.수량만 변경해서
    - option 있으면 option까지 동일하면 get으로 
                            option이 다르면 new로,,
    2. bidding
    - 그냥 바로 filter 없으면 바로 get
    '''
 
    try:
        at_cart = request.POST.get('at_cart')
        only_add = False
    except:
        at_cart = False
        only_add = True
    user = request.user
    
    product_type = request.POST.get('product_type')

    # 1. 카트에서 remove가 호출된 경우
    if at_cart:
        '''
        카트에서 호출된 경우
        1. cart_item_id 받고
        2. cart_item_obj 받고
        3. 지우면 지우고 아니면 그냥 추가하고.
        4. return redirect
        '''
        cart_item_id = request.POST.get('cart_item_id')

        cart_obj, new_obj = Cart.objects.new_or_get(request)
        cart_item_obj, new_item_obj = CartItem.objects.new_or_get(request)
        
        if cart_item_obj in cart_obj.cart_items.all():
            cart_item_obj.add_certificate = False
            cart_item_obj.save()
            cart_obj.cart_items.remove(cart_item_obj)
            added = False
            cart_obj.save()
            cart_item_obj.delete()
            # 부득이하게 여기에 cart_item계산을 한번 더 넣는다... jquery잘하게 되면 다시 구현하자.
            request.session['cart_items'] = cart_obj.cart_items.count()
            return redirect("carts:home")
        else:
            return redirect("carts:home")
    else:
        # 2. 물품추가 혹은 티켓구매인경우
        product_item_id = request.POST.get('product_item_id', None) # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
        option = request.POST.get('option', None)
        tickets_type = request.POST.get('tickets_type', None)
        
        if product_type == 'bidding' or product_type == 'normal':
            # product_item_id = request.POST.get('product_item_id') # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
            # option = request.POST.get('option', None)
            product_item_obj = ProductItem.objects.get(id=product_item_id)

            # ticket_item_id = None
            
        elif product_type == 'ticket':
            # tickets_type = request.POST.get('tickets_type')
            # ticket_item_obj = TicketItem.objects.get(id=ticket_item_id)
            ticket_item_obj = TicketItem.objects.new(user=user, tickets_type=tickets_type)
            ticket_item_id = ticket_item_obj.id
            
            ticket_item_obj.save()

            # product_item_id = None
        else:
            raise Http404("직원님...해당물품의 아이디가 이상합니다.") 


        # 추가수량에 대해 POST로 오면 업뎃
        # 이부분이 product_type으로 if문을 추가로 안에 넣을지는 고민 필요.
        if product_type == "bidding":
            amount = 1 # 경매상품일때
        elif product_type == "normal":
            amount = request.POST.get('amount') # 상시상품일때
            if amount == '' or amount == '---' or amount == '재고없음':
                print("사이즈와 수량이 입력되지 않았다.")
                # return 
                messages.error(request, "사이즈와 구매수량을 넣어주세요.")
                return redirect('products:product_detail', slug=product_item_obj.slug)
        elif product_type == 'ticket':
            amount = 1

        if product_item_id is not None or ticket_item_id is not None:
            if product_item_id is not None:
                temp_id = product_item_id
            elif ticket_item_id is not None:
                temp_id = ticket_item_id
            cart_obj, new_obj = Cart.objects.new_or_get(request)
            cart_item_obj, new_item_obj = CartItem.objects.new_or_get(request, temp_id)
            
            
            # 2. 그냥 추가 혹은 수량조정인경우
            # m2m Change가 적용되려면 cart_item의 수량과 단가가 확정되어야함.
            
            # 단가확정
            if product_type == "bidding":
                price = Bidding.objects.get(user=user, product_item=cart_item_obj.product_item, win=True).bidding_price
            elif product_type == "normal":
                price = product_item_obj.price
            elif product_type == "ticket":
                price = ticket_item_obj.total

            cart_item_obj.price = price
            cart_item_obj.amount = amount
            cart_item_obj.save()

            if cart_item_obj in cart_obj.cart_items.all() and only_add:
                # m2mchange가 안되서 그냥 지웠다가 다시 추가함.
                cart_obj.cart_items.remove(cart_item_obj)
                cart_obj.cart_items.add(cart_item_obj)
                added = False
                cart_obj.save()
            # 처음 추가되는 cart_item일경우
            else:
                cart_obj.cart_items.add(cart_item_obj)
                added = True
                cart_obj.save()
                
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
        # return HttpResponseRedirect("carts:home")


def checkout_iamport_now(request):
    '''
    바로구매

    1. normal, bidding 
    - 그냥 있는그대로 카트에 있는거 구매.
    - rental 지우기

    2. rental
    - rental 빼고 다지우기.
    - 왜냐면 rental은 한가지 항목에 대해 기간도 넣어서 구매해야하기 때문에.

    '''

    print("체크아웃나웃 실행")
    product_type = request.POST.get('product_type')

    
    # 2. 물품추가 혹은 티켓구매인경우
    product_item_id = request.POST.get('product_item_id', None) # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
    option = request.POST.get('option', None)
    tickets_type = request.POST.get('tickets_type', None)
    
    if product_type == 'bidding' or product_type == 'normal' or product_type == 'rental':
        # product_item_id = request.POST.get('product_item_id') # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
        # option = request.POST.get('option', None)
        product_item_obj = ProductItem.objects.get(id=product_item_id)

        # ticket_item_id = None
        
    elif product_type == 'ticket':
        # tickets_type = request.POST.get('tickets_type')
        # ticket_item_obj = TicketItem.objects.get(id=ticket_item_id)
        ticket_item_obj = TicketItem.objects.new(user=user, tickets_type=tickets_type)
        ticket_item_id = ticket_item_obj.id
        
        ticket_item_obj.save()

        # product_item_id = None
    else:
        raise Http404("직원님...해당물품의 아이디가 이상합니다.") 


    # 추가수량에 대해 POST로 오면 업뎃
    # 이부분이 product_type으로 if문을 추가로 안에 넣을지는 고민 필요.
    if product_type == "bidding":
        amount = 1 # 경매상품일때
    elif product_type == "normal" or product_type == "rental" :
        amount = request.POST.get('amount') # 상시상품일때
        if amount == '' or amount == '---' or amount == '재고없음':
            print("사이즈와 수량이 입력되지 않았다.")
            # return 
            messages.error(request, "사이즈와 구매수량을 넣어주세요.")
            return redirect('products:product_detail', slug=product_item_obj.slug)
    elif product_type == 'ticket':
        amount = 1

    if product_item_id is not None or ticket_item_id is not None:
        if product_item_id is not None:
            temp_id = product_item_id
        elif ticket_item_id is not None:
            temp_id = ticket_item_id

        # 렌탈물품이면 cart 무조건 새로 만들어라.
        if product_type == 'rental':
            del request.session['cart_id']
            cart_obj, new_obj = Cart.objects.new_or_get(request)
        # 렌탈물품이 아니면 렌탈물품이 기존에 있는것을 다 지워라. (헷갈리쟈나.)
        else:
            cart_obj, new_obj = Cart.objects.new_or_get(request)
            for cart_item_obj in cart_obj.cart_items.all():
                if cart_item_obj.product_type == 'rental':
                    cart_item_obj.delete()
        print('체크아웃 아임포트 나우에서 뉴올겟 직전열 395')
        cart_item_obj, new_item_obj = CartItem.objects.new_or_get(request, temp_id)
        
        
        # 2. 그냥 추가 혹은 수량조정인경우
        # m2m Change가 적용되려면 cart_item의 수량과 단가가 확정되어야함.
        
        # 단가확정
        if product_type == "bidding":
            price = Bidding.objects.get(user=user, product_item=cart_item_obj.product_item, win=True).bidding_price
        elif product_type == "normal":
            price = product_item_obj.price
        elif product_type == "ticket":
            price = ticket_item_obj.total
        elif product_type == 'rental':
            price = product_item_obj.price

        cart_item_obj.price = price
        cart_item_obj.amount = amount
        cart_item_obj.save()

        if cart_item_obj in cart_obj.cart_items.all():# and only_add:
            # m2mchange가 안되서 그냥 지웠다가 다시 추가함.
            cart_obj.cart_items.remove(cart_item_obj)
            cart_obj.cart_items.add(cart_item_obj)
            added = False
            cart_obj.save()
        # 처음 추가되는 cart_item일경우
        else:
            cart_obj.cart_items.add(cart_item_obj)
            added = True
            cart_obj.save()
            
        # 그냥 나중에 쓸수도 있는 json이기에 남겨둠.
        request.session['cart_items'] = cart_obj.cart_items.count()
        request.session['checkout_iamport_now'] = True
    # return True
    print("리다이렉트 넘어간다.", cart_item_obj.id)
    return redirect("carts:checkout-iamport")

@login_required
def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {})

@login_required
def checkout_fail_view(request):
    return render(request, "carts/checkout-fail.html", {})

@login_required
def checkout_vbank_view(request):
    return render(request, "carts/checkout-vbank.html", {})


#############아임포트로 체크아웃 재구현###################

@login_required
def checkout_iamport(request, *args, **kwargs):
    '''
    크게 보면 체크아웃절차는 아래와 같이 이루어짐
    1. 카트 만듬.
    2. 빌링프로파일 만듬. -> order 만듬.
    3. 빌링주소, 쉬핑주소 만듬. -> 깆고오고 없으면 만듬
    4. order에 위 3개 붙이기.
    5. 결제쪽으로 넘어가기.
    6. 결재쪽 POST 3가지 1) 체크아웃눌렀을떄, 2) 포인트사용 눌렀을때 3) 주소 변경 눌렀을때.
    7. 위의 각각을 처리할수 있게 POST에다가 post_purpose를 달아서 진행ㅎ시키자.
    
    원래 페이지는 3번정도로 나눠서 진행하고 있지만 지금은 한페이지에서 한번에 진행되게 할 것이다. 
    주소는 2개주소가 없으면 폼입력으로 뜨게 할거고 있으면 그냥 현황을 보여주고 수정버튼을 달아 수정이 가능하게 하려고 한다.
    그럼 진행해보자. 

    '''

    # 바로구매인지 확인을 위함.
    # try:
    #     checkout_iamport_now(request)
    # except:
    #     pass

    # 바로구매시 checkoutnow에서 옴
    checkout_directly = request.session.get('checkout_iamport_now', None)
    # 바로 구매 세션 삭제
    if checkout_directly is not None:
        del request.session['checkout_iamport_now']
    #############################################################################
    # 지금 상황.
    # 체크아웃 다이렉틀리 때문에 첫화면 로드로 자꾸간다. 
    # 체크아웃다이렉틀리는 1회성이어야한다. 
    # 그래서 아무래도 세션을 삭제를 해주긴해야할듯. 
    # 단 어드레스수정. 포인트 어쩌구등에서는 다시 만들어주고
    # 결제가 직접적으로 될때는 안만들어주자.
    # 그래야 넘어가든 말든할듯하다. 
    # 졸리다. 
    ############################################################################


    # 1. 카트만들기.(없으면 만들고 있으면 있는거 갖겨오고 재고 없는것 체크, 없으면 지우기)

    
    user = request.user
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.cart_items.count() == 0:
        return redirect("carts:home")   
    # login_form = LoginForm(request=request)
    # guest_form = GuestForm(request=request)
    # address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)
    # 물건들의 재고가 남아있는지 check
    # order_obj = request.POST.get('order_obj')
    stock_refresh = False # 괜찮으면 넘어가고 안괜찮으면 스탁없는 물품들을 refresh하기 위해 carts:home 보냄.
    for cart_item_obj in cart_obj.cart_items.all():
        print("Stock Check...product.title")
        if cart_item_obj.product_type == 'normal':
            if cart_item_obj.option is not None:
                option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
                if option_obj.amount < 1 or not cart_item_obj.product_item.featured:
                    print('{}의 재고가 없어 카트에서 제거합니다.'.format(cart_item_obj.product_item.product.title))
                    messages.success(request, '{}의 재고가 없어 카트에서 제거합니다.'.format(cart_item_obj.product_item.product.title))
                    cart_obj.cart_items.remove(cart_item_obj)
                    cart_obj.save()
                    cart_item_obj.delete()
                    stock_refresh = True
            else:
                if cart_item_obj.product_item.amount < 1 or not cart_item_obj.product_item.featured:
                    print('{}의 재고가 없어 카트에서 제거합니다.'.format(cart_item_obj.product_item.product.title))
                    messages.success(request, '{}의 재고가 없어 카트에서 제거합니다.'.format(cart_item_obj.product_item.product.title))
                    cart_obj.cart_items.remove(cart_item_obj)
                    cart_obj.save()
                    cart_item_obj.delete()
                    stock_refresh = True
        else:
            pass
    if stock_refresh:
        return redirect("carts:home")

    # 2. 빌링프로파일 만들기
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    shipping_address_obj = None
    billing_address_obj = None

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        # if shipping_address_id:
        if address_qs.filter(address_type='shipping').count() > 0:
            # order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            # del request.session['shipping_address_id']
            shipping_address_obj = address_qs.filter(address_type='shipping').order_by('-timestamp').first()
            order_obj.shipping_address = shipping_address_obj
            
            print("shipping_address가 존재합니다.")
        else:
            shipping_address_obj = None
            print("shipping_address가 없습니다.")


        if address_qs.filter(address_type='billing').count() > 0:
            # order_obj.billing_address = Address.objects.get(id=billing_address_id)
            # del request.session['billing_address_id']
            billing_address_obj = address_qs.filter(address_type='billing').order_by('-timestamp').first()
            order_obj.billing_address = billing_address_obj
        else:
            billing_address_obj = None

        order_obj.update_total()
        order_obj.customer_request = "없음"
        order_obj.save()




    
    # 3.  첫 화면 로드 - 주소2개 있을때
    # 주소는 완성되어있게 하고 빌링 주소, 쉬핑주소 같이 나오게(위아래로,)
    # 오른쪽에 장바구니항목간단표기 및 포읹트 사용가능하게 나옴. 
    # 아직 포스트를 누르지는 않았음.
    
    point_available = None
    order_normal_total = 0
    for cart_item in order_obj.cart.cart_items.all():
        if cart_item.product_type == 'normal' or cart_item.product_type == 'rental' :
            order_normal_total = order_normal_total + cart_item.subtotal
    point_available = round(order_normal_total * 1, -2)
    if point_available >= user.points:
        point_available = user.points
    else:
        pass
    print('point_available',point_available)


    # 첫화면에서 결제를 할 수 있기때문에 주소 유효성을 확인하자.
    if shipping_address_obj:
        address = shipping_address_obj.get_address()
        postcode = shipping_address_obj.get_postal_code()
    else:
        address = None
        postcode = None

    # 결제시 필요한 name에 물건들을 넣어주자.
    cart_items_name = "" # 실제 물품명
    cart_items_name_iamport = "" # 아임포트용 물품명 -> 티켓내용 제외
    item_count = cart_obj.cart_items.all().count()
    for i, cart_item in enumerate(cart_obj.cart_items.all()):
        if cart_item.product_type == 'ticket':
            cart_items_name = cart_items_name + "ticket_" + str(cart_item.ticket_item.tickets_type)
            if i < item_count-1:
                cart_items_name = cart_items_name + ", "
        else:
            cart_items_name = cart_items_name + cart_item.product_item.product.title
            cart_items_name_iamport = cart_items_name_iamport + cart_item.product_item.product.title
            if i < item_count-1:
                cart_items_name = cart_items_name + ", "
                cart_items_name_iamport = cart_items_name_iamport + ", "
        
        if len(cart_items_name) > 200:
            cart_items_name = cart_items_name[:200] + "..."


    
    # 도서산간지역이면 배송비용추가함. #
    # 빌링프로파일에 어드레스가 없는 이제 막 만들어진 상태에서는 배송비용에 대한 정보 아직 없어도됨.
    # 어드레스가 있는지 확인해서 있으면 아래의 프로세스 진행.
    if postcode is not None:
        postal_code = postcode
        print('배송갯수')
        df_postal_code  = pd.read_csv(POSTAL_CODE_INFORMATION_DIRS)
        postal_code_array = df_postal_code.postal_code.values
        
        # 배송갯수 세기
        delivery_count = 0
        combined_delevery_exist = False
        for cart_item in cart_obj.cart_items.all():
            if cart_item.product_type == 'normal' or cart_item.product_type == 'bidding' or cart_item.product_type == 'rental':
                if not cart_item.product_item.product.combined_delivery:
                    delivery_count += 1
                else:
                    combined_delevery_exist = True
        if combined_delevery_exist:
            delivery_count += 1
        order_obj.shipping_count = delivery_count
            
        if str(postal_code) in postal_code_array:
            order_obj.shipping_cost = 3000 * delivery_count
        else:
            order_obj.shipping_cost = 0
        
        order_obj.update_total()
    ###############################################
    # 빌링프로파일의 카드를 acitve로 셋팅해주자.
    card_qs = Card.objects.filter(user=user, active=True)
    if card_qs.count() == 1:
        card_obj = card_qs.first()
        billing_profile.card = card_obj
        billing_profile.save()
    else:
        billing_profile.card = None
        billing_profile.save()

    context = {
        'object':order_obj,
        'billing_profile': billing_profile,
        'shipping_address_obj': shipping_address_obj,
        'billing_address_obj': billing_address_obj,
        'address_qs': address_qs,
        'base_url': getattr(settings, 'BASE_URL', 'https://moum8.com'),
        # 'address_changed': False,

        # 결재용 context
        'pg': "html5_inicis.INIpayTest",
        'pay_method':'card',
        'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
        'name':cart_items_name_iamport,
        'amount': order_obj.checkout_total,
        'buyer_email': billing_profile.email,
        'buyer_name': user.full_name,
        'buyer_tel': user.phone_number,# 얘는 만들어야함. 
        'buyer_addr': address,
        'buyer_postcode': postcode,
        # 포인트관련 
        # 'point_changed': False,
        'point_available': point_available
        #  저장된 빌링키로 결제시

        }
    if order_obj.billing_profile.card is not None:
        context['customer_uid']: order_obj.billing_profile.card.customer_uid


    post_purpose = request.POST.get('post_purpose', None)
    print('post_purpose', post_purpose)
    # 항상 이것으로 끝나게 하면 안되므로 POST가 아니면 아래와 같이 진행되게 하자. 
    # 주소가 있는경우와 없는경우로 나눠지는데 둘다 이후에는 POST를 누를거기 때문에 이렇게 하면 첫화면 구성은 끝날거같다.
    

    # 아임포트 토큰 가져오기
    

    # 원래위치 여기 하지만 맨마지막으로 최초화면 로딩을 옮긴다.################################################
    # if request.method == 'POST' and not post_purpose and not request.is_ajax() or checkout_directly:
    #     print('체크아웃 최초화면 로딩')
    #     print('context', context)

    #     # 바로구매의 get으로 인한 http404 방지용
    #     # 결제가 됐을때는 아래의 session이 없어져도 상관없다. 
    #     # 하지만 결제가 안됐을때 checkout_iamport는 get으로 오게되어 모바일결제로 넘어오게 된다. 
    #     # 이것을 방지하기 위해 아래와 같이 다시 session을 만들어 첫화면이 보이게 해준다.
    #     request.session['checkout_iamport_now'] = True
    #     return render(request, "carts/checkout-iamport.html", context)
    # 원래위치 여기 하지만 맨마지막으로 최초화면 로딩을 옮긴다.################################################



    # 4. POST 이후의 화면 구성
    #   1) 주소 수정 눌렀을 때
    #   2) 포인트사용 눌렀을 떄
    #   3) 최종 결재를 눌렀을 때
    # 단 어떤 경우든 바로 결재가 진행될 수 있어야함. 주소가 없는경우를 따로 가정하지는 말자. 그떄는 버튼을 없에버리면 될듯.
    
    iamport = Iamport(imp_key=IMPORT_REST_API_KEY, imp_secret=IMPORT_REST_API_SECRET)
    user = request.user
    # 1) 주소 수정 눌렀을 때
    if request.method == 'POST' and post_purpose == 'change_or_add_address':
        full_name   = request.POST.get('full_name', None)
        email       = request.POST.get('email', None)
        if email == "":
            email = user.email
        phone_number = request.POST.get('phone_number', None)
        address_line_1 = request.POST.get('address_line_1', None)
        address_line_2 = request.POST.get('address_line_2', None)
        postal_code = request.POST.get('postal_code', None)
        order_memo = request.POST.get('order_memo', None)
        if order_memo == "" or order_memo is None:
            order_memo == "없음"

        # address_type = request.POST.get('address_type', None)
        
        # 폼이 제대로 완성되어있지 않았을 경우
        print(full_name, email, phone_number, address_line_1, address_line_2, postal_code, order_memo)
        if not full_name or not address_line_1 or not address_line_2 or not postal_code:
            change_address = True
            if full_name is None or full_name == '':
                messages.success(request, '수령인 이름이 입력되지 않았습니다.')
            elif phone_number is None or phone_number == '':
                messages.success(request, '전화번호가 입력되지 않았습니다.')
            elif address_line_1 is None or address_line_1 == '':
                messages.success(request, '주소가 입력되지 않았습니다.')
            elif address_line_2 is None or address_line_2 == '':
                print('address_line_2',address_line_2)
                messages.success(request, '상세주소가 입력되지 않았습니다.')
            elif postal_code is None or postal_code == '':
                messages.success(request, '우편번호가 입력되지 않았습니다.')
            # return render(request, "carts/checkout-iamport.html", context)
            # return redirect("carts:checkout-iamport")
        elif not shipping_address_obj:
            shipping_address_obj = Address.objects.create(billing_profile=billing_profile,
                                                            address_type='shipping', 
                                                            full_name=full_name,
                                                            email=email,
                                                            phone_number=phone_number,
                                                            address_line_1=address_line_1,
                                                            address_line_2=address_line_2,
                                                            postal_code=postal_code
                                                            )
            billing_address_obj = Address.objects.create(billing_profile=billing_profile,
                                                            address_type='billing', 
                                                            full_name=full_name,
                                                            email=email,
                                                            phone_number=phone_number,
                                                            address_line_1=address_line_1,
                                                            address_line_2=address_line_2,
                                                            postal_code=postal_code
                                                            )
            # address_changed = True
            # point_changed = False
            change_address = False
            print("Address created.")
            messages.success(request, "배송지 정보가 만들어졌습니다.")
        else:
            shipping_address_obj.full_name = full_name
            shipping_address_obj.email = email
            shipping_address_obj.phone_number = phone_number
            shipping_address_obj.address_line_1 = address_line_1
            shipping_address_obj.address_line_2 = address_line_2
            shipping_address_obj.postal_code = postal_code
            
            shipping_address_obj.save()
            
        # 여기에 postal_code에 따른 배송비용이 추가됨.
        # 1) 각물품의 갯수를 파악(합배송가능한건 합해서 1, 나머지는 개별 1로 침.)
        # 2) postal_code가 산지배송이면 * 5000원으로 order_obj의 shipping_cost에 추가.
        # 3) order_obj의 총 checkout 비용에 shipping_cost 추가.
        

        # 도서산간지역이면 배송비용추가함. ##############
        print('배송갯수')
        df_postal_code  = pd.read_csv(POSTAL_CODE_INFORMATION_DIRS)
        postal_code_array = df_postal_code.postal_code.values
        # 배송갯수 세기
        delivery_count = 0
        combined_delevery_exist = False
        for cart_item in cart_obj.cart_items.all():
            if cart_item.product_type == 'normal' or cart_item.product_type == 'bidding':
                if not cart_item.product_item.product.combined_delivery:
                    delivery_count += 1
                else:
                    combined_delevery_exist = True
        if combined_delevery_exist:
            delivery_count += 1
        order_obj.shipping_count = delivery_count
            
        if str(postal_code) in postal_code_array:
            order_obj.shipping_cost = 3000 * delivery_count
        else:
            order_obj.shipping_cost = 0
        
        order_obj.update_total()
        order_obj.customer_request = order_memo
        ###############################################


        change_address = False # 주소변경 완료됐으므로 템플릿에 체인지 하자 안해도됨.
        # address_changed = True
        # point_changed = False
        print("Address changed")
        messages.success(request, "배송지 정보가 수정되었습니다.")

        
        context = {
            'object':order_obj,
            'billing_profile': billing_profile,
            'shipping_address_obj': shipping_address_obj,
            'billing_address_obj': billing_address_obj,
            'address_qs': address_qs,
            # 'address_changed': address_changed,
            'change_address': change_address,
            'base_url': getattr(settings, 'BASE_URL', 'https://moum8.com'),

            # 결재용 context
            'pg': "html5_inicis.INIpayTest",
            'pay_method':'card',
            'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
            'name':cart_items_name_iamport,
            'amount': order_obj.checkout_total,
            'buyer_email': billing_profile.email,
            'buyer_name': user.full_name,
            'buyer_tel': user.phone_number,# 얘는 만들어야함. 
            'buyer_addr': address,
            'buyer_postcode': postcode,
            # 포인트관련
            # 'point_changed': point_changed,
            'point_available': point_available
            }
        return render(request, "carts/checkout-iamport.html", context)
    elif request.method == 'POST' and post_purpose == 'modify_address':
        print('체크아웃 주소수정화면 로딩')

        # 바로구매의 get으로 인한 http404 방지용
        # 결제가 됐을때는 아래의 session이 없어져도 상관없다. 
        # 하지만 결제가 안됐을때 checkout_iamport는 get으로 오게되어 모바일결제로 넘어오게 된다. 
        # 이것을 방지하기 위해 아래와 같이 다시 session을 만들어 첫화면이 보이게 해준다.
        request.session['checkout_iamport_now'] = True
        
        # address_changed = False
        # point_changed = False
        context = {
            'object':order_obj,
            'billing_profile': billing_profile,
            'shipping_address_obj': shipping_address_obj,
            'billing_address_obj': billing_address_obj,
            'address_qs': address_qs,
            # 'address_changed': address_changed,
            'change_address': True,
            'base_url': getattr(settings, 'BASE_URL', 'https://moum8.com'),

            # 결재용 context
            'pg': "html5_inicis.INIpayTest",
            'pay_method':'card',
            'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
            'name':cart_items_name_iamport,
            'amount': order_obj.checkout_total,
            'buyer_email': billing_profile.email,
            'buyer_name': user.full_name,
            'buyer_tel': user.phone_number,# 얘는 만들어야함. 
            'buyer_addr': address,
            'buyer_postcode': postcode,
            # 포인트관련
            # 'point_changed': point_changed,
            'point_available': point_available
            }
        return render(request, "carts/checkout-iamport.html", context)    

    
    # 2) 포인트사용 버튼 눌렀을 때
    elif request.method == 'POST' and post_purpose == 'use_point':
        print('체크아웃 포인트사용적용')

        # 바로구매의 get으로 인한 http404 방지용
        # 결제가 됐을때는 아래의 session이 없어져도 상관없다. 
        # 하지만 결제가 안됐을때 checkout_iamport는 get으로 오게되어 모바일결제로 넘어오게 된다. 
        # 이것을 방지하기 위해 아래와 같이 다시 session을 만들어 첫화면이 보이게 해준다.
        request.session['checkout_iamport_now'] = True

        use_point = request.POST.get('use_point')
        print('usepoint.', use_point)
        if use_point == '':
            use_point = 0
        # print('포인트사용하려고 하긴한다.', 554, '하지만 문제가 생긴다.')
        try:
            order_obj.point_total = int(use_point)
            order_obj.checkout_total = order_obj.total - int(use_point)
            order_obj.update_total()
            order_obj.save()
            messages.error(request, "{}POINT 사용이 반영되었습니다.".format(use_point))
            context = {
                'object':order_obj,
                'billing_profile': billing_profile,
                'shipping_address_obj': shipping_address_obj,
                'billing_address_obj': billing_address_obj,
                'address_qs': address_qs,
                # 'address_changed': False,
                'base_url': getattr(settings, 'BASE_URL', 'https://moum8.com'),

                # 결재용 context
                'pg': "html5_inicis.INIpayTest",
                'pay_method':'card',
                'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
                'name':cart_items_name_iamport,
                'amount': order_obj.checkout_total,
                'buyer_email': billing_profile.email,
                'buyer_name': user.full_name,
                'buyer_tel': user.phone_number,# 얘는 만들어야함. 
                'buyer_addr': address,
                'buyer_postcode': postcode,
                # 포인트관련 
                # 'point_changed': False,
                'point_available': point_available

                }
            return render(request, "carts/checkout-iamport.html", context)
        except:
            messages.error(request, "사용하려는 POINT를 다시 입력해주세요.")
            return render(request, "carts/checkout-iamport.html", context)

            # return HttpResponse("HTTP respone가 뭐쟈")
        
    # 3) 결재할 금액이 포인트로 다 대체 되었을 경우
    elif request.method == 'POST' and post_purpose == 'checkout_0':
        print('체크아웃 포인트로 전체결제')
        order_obj.mark_paid()
        request.session['cart_items'] = 0
        del request.session['cart_id']
        
        # 사용포인트 차감
        if order_obj.point_total > 0:
            point_use = (-1) * order_obj.point_total
            point_details = "주문번호 {} 구매를 위한 포인트 {} 사용".format(order_obj, point_use)
            point_obj = Point.objects.new(user=user, amount=order_obj.point_total, details=point_details)
        # 재고 있는것들에 대해서 아래와 같이 구매한다.
        for cart_item_obj in cart_obj.cart_items.all():
            if cart_item_obj.product_type == 'normal':
                if cart_item_obj.option is not None:
                    option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
                    option_obj.amount = option_obj.amount - cart_item_obj.amount
                    option_obj.save()
                    print('{}의 {}옵션이 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, option_obj.option, option_obj.amount))                 
                else:
                    cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - cart_item_obj.amount
                    cart_item_obj.product_item.save()
                    print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))
        order_address_obj = OrderAddress.objects.create(
            user=user,
            email=order_obj.shipping_address.email,
            phone_number=order_obj.shipping_address.phone_number,
            full_name=order_obj.shipping_address.full_name,
            address_line_1=order_obj.shipping_address.address_line_1,
            address_line_2=order_obj.shipping_address.address_line_2,
            postal_code=order_obj.shipping_address.postal_code,   
        )
        order_obj.final_address = order_address_obj
        order_obj.cart_items_name = cart_items_name
        order_obj.save()

        context = {
        'object':order_obj,
        'billing_profile': billing_profile,
        'shipping_address_obj': shipping_address_obj,
        'billing_address_obj': billing_address_obj,
        'address_qs': address_qs,
        # 'address_changed': False,
        'base_url': getattr(settings, 'BASE_URL', 'https://moum8.com'),

        # 결재용 context
        'pg': "html5_inicis.INIpayTest",
        'pay_method':'card',
        'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
        'name':cart_items_name_iamport,
        'amount': order_obj.checkout_total,
        'buyer_email': billing_profile.email,
        'buyer_name': user.full_name,
        'buyer_tel': user.phone_number,# 얘는 만들어야함. 
        'buyer_addr': address,
        'buyer_postcode': postcode,
        # 포인트관련 
        # 'point_changed': False,
        'point_available': point_available

        }

        return render(request, 'carts/checkout-done.html', {})
        
        # 4) 마지막으로 결재버튼이 눌렸을 경우
    elif request.method == 'POST' and request.is_ajax():
        print('체크아웃 일반결제 모듈 후 ajax 요청.')
        imp_uid = request.POST.get('imp_uid', None)
        # customer_uid = request.POST.get('customer_uid', None)
        # merchant_uid = request.POST.get('merchant_uid', None)
        # amount = request.POST.get('amount', None)

        # if customer_uid is None:
        #     response = iamport.find(imp_uid=imp_uid)
        #     merchant_uid = response['merchant_uid']
        #     order_amount = order_obj.checkout_total
        #     is_paid = iamport.is_paid(order_amount, merchant_uid=merchant_uid)
        #     status = response['status']
        response = iamport.find(imp_uid=imp_uid)
        merchant_uid = response['merchant_uid']
        order_amount = order_obj.checkout_total
        is_paid = iamport.is_paid(order_amount, merchant_uid=merchant_uid)
        status = response['status']


        if is_paid:
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
                
                
                # 사용포인트 차감
                if order_obj.point_total > 0:
                    point_use = (-1) * order_obj.point_total
                    point_details = "주문번호 {} 구매를 위한 포인트 {} 사용".format(order_obj, point_use)
                    point_obj = Point.objects.new(user=user, amount=point_use, details=point_details)


                # 재고 있는것들에 대해서 아래와 같이 구매한다.
                for cart_item_obj in cart_obj.cart_items.all():
                    if cart_item_obj.product_type == 'normal':
                        if cart_item_obj.option is not None:
                            option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
                            option_obj.amount = option_obj.amount - cart_item_obj.amount
                            option_obj.save()
                            print('{}의 {}옵션이 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, option_obj.option, option_obj.amount))                 
                        else:
                            cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - cart_item_obj.amount
                            cart_item_obj.product_item.save()
                            print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))
                
                # 최종 주소 저장 및 charge 만들기
                order_address_obj = OrderAddress.objects.create(
                    user=user,
                    email=order_obj.shipping_address.email,
                    phone_number=order_obj.shipping_address.phone_number,
                    full_name=order_obj.shipping_address.full_name,
                    address_line_1=order_obj.shipping_address.address_line_1,
                    address_line_2=order_obj.shipping_address.address_line_2,
                    postal_code=order_obj.shipping_address.postal_code,   
                )
                order_obj.final_address = order_address_obj
                order_obj.cart_items_name = cart_items_name
                order_obj.save()
                charge_obj = Charge.objects.new(order=order_obj, response=response)

                # 결제 성공하여 이메일 보내기
                order_complete_mail(user.email, order_obj)
                alimtalk_message = '''{user}님이 구매하신 상품의 결제가 완료되었습니다.

물품: {cart_items_name}
총 금액: {checkout_total}
'''.format(user=user, cart_items_name=cart_items_name_iamport, checkout_total=order_obj.checkout_total)
                send(templateCode='alim3', to=user.phone_number, message=alimtalk_message)
                print("{}으로 결제완료 알림톡이 보내졌습니다.".format(user.phone_number))

                return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
                                    content_type="application/json")
            else:
                print("결재 상태 : 결제가 실패하였습니다.")
                return HttpResponse(json.dumps({'status': "fail", 'message': "결제 실패"}), content_type="application/json")
        else:
            print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
            return HttpResponse(json.dumps({'status': "forgery", 'message': "위조된 결제시도"}), content_type="application/json") 
    
    elif request.method == 'POST' and post_purpose == 'simple_checkout':
        print('체크아웃 간편결제')
        imp_uid = request.POST.get('imp_uid', None)
        customer_uid = request.POST.get('customer_uid', None)
        merchant_uid = request.POST.get('merchant_uid', None)
        amount = request.POST.get('amount', None)
        name = request.POST.get('name', None)
        payload = {
            'customer_uid': customer_uid,
            'merchant_uid': merchant_uid,
            'amount': order_obj.checkout_total,
            'name': name,
        }
        print('payload', payload)
        response = iamport.pay_again(**payload)
        print('response', response)
        order_amount = order_obj.checkout_total
        is_paid = iamport.is_paid(order_amount, merchant_uid=merchant_uid)
        status = response['status']

        if is_paid:
            # DB에 결제 정보 저장
            # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
            # if status == 'ready':
            #     # DB에 가상계좌 발급정보 저장
            #     print("결재 상태 : ready, vbankIssued")
            #     return HttpResponse(json.dumps({'status': "vbankIssued", 'message': "가상계좌 발급 성공"}),
            #                         content_type="application/json")
            if status=='paid':
                print("결재 상태 : paid, success")

                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                
                
                # 사용포인트 차감
                if order_obj.point_total > 0:
                    point_use = (-1) * order_obj.point_total
                    point_details = "주문번호 {} 구매를 위한 포인트 {} 사용".format(order_obj, point_use)
                    point_obj = Point.objects.new(user=user, amount=point_use, details=point_details)


                # 재고 있는것들에 대해서 아래와 같이 구매한다.
                for cart_item_obj in cart_obj.cart_items.all():
                    if cart_item_obj.product_type == 'normal':
                        if cart_item_obj.option is not None:
                            option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
                            option_obj.amount = option_obj.amount - cart_item_obj.amount
                            option_obj.save()
                            print('{}의 {}옵션이 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, option_obj.option, option_obj.amount))                 
                        else:
                            cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - cart_item_obj.amount
                            cart_item_obj.product_item.save()
                            print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))
                
                # 최종 주소 저장 및 charge 만들기
                order_address_obj = OrderAddress.objects.create(
                    user=user,
                    email=order_obj.shipping_address.email,
                    phone_number=order_obj.shipping_address.phone_number,
                    full_name=order_obj.shipping_address.full_name,
                    address_line_1=order_obj.shipping_address.address_line_1,
                    address_line_2=order_obj.shipping_address.address_line_2,
                    postal_code=order_obj.shipping_address.postal_code,   
                )
                order_obj.final_address = order_address_obj
                order_obj.cart_items_name = cart_items_name
                order_obj.save()
                charge_obj = Charge.objects.new(order=order_obj, response=response)
                # print(response)
                order_complete_mail(user.email, order_obj)
                alimtalk_message = '''{user}님이 구매하신 상품의 결제가 완료되었습니다.

물품: {cart_items_name}
총 금액: {checkout_total}
'''.format(user=user, cart_items_name=cart_items_name_iamport, checkout_total=order_obj.checkout_total)
                send(templateCode='alim3', to=user.phone_number, message=alimtalk_message)
                print("{}으로 결제완료 알림톡이 보내졌습니다.".format(user.phone_number))
                return redirect('carts:success')
            else:
                print("결재 상태 : 결제가 실패하였습니다.")
                return redirect('carts:home')
                # return HttpResponse(json.dumps({'status': "fail", 'message': "결제 실패"}), content_type="application/json")
        else:
            print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
            return redirect('carts:home')
    

    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★여기완성시켜야해.
    # 렌탈 물품일경우.(렌탈은 무조건 예약결제이므로 카드등록이 되어있어야함.)
    elif request.method == 'POST' and post_purpose == 'rental':
        print('체크아웃 렌탈 결제예약 설정')
        imp_uid = request.POST.get('imp_uid', None)
        customer_uid = request.POST.get('customer_uid', None)
        merchant_uid = request.POST.get('merchant_uid', None)
        amount = request.POST.get('amount', None)
        name = request.POST.get('name', None)

        rental_start_date = order_obj.cart.cart_items.first().rental_start_date
        period = order_obj.cart.cart_items.first().period
        schedule_list = []


        from django.utils import timezone
        import time
        import datetime

        for i in range(0, period):
            schedule = rental_start_date + datetime.timedelta(days=i)
            schedule_timestamp = time.mktime(schedule.timetuple())
            schedule_list.append(schedule_timestamp)

        payload = {
            'customer_uid': customer_uid,
            'schedules': [
            ]
        }

        for schedule in schedule_list:
            schedule_dict = {
                'merchant_uid': merchant_uid,
                # UNIX timestamp
                'schedule_at': schedule,
                'amount': order_obj.checkout_total,
                'name': order_obj.cart_items_name,
                'buyer_name': order_obj.shipping_address.full_name,
                'buyer_email': order_obj.shipping_address.email,
                'buyer_tel': order_obj.shipping_address.phone_number,
                'buyer_addr': order_obj.shipping_address.get_address(),
                'buyer_postcode': order_obj.shipping_address.postal_code,
                }
            payload['schedules'].append(schedule_dict)

        print('payload', payload)

        # response = iamport.pay_schedule(**payload)
        # print('response', response)
        try:
            response = iamport.pay_schedule(**payload)
            print('response', response)
            
            # 예약 성공 시
            order_obj.is_rental = True
            order_obj.save()

            order_address_obj = OrderAddress.objects.create(
                    user=user,
                    email=order_obj.shipping_address.email,
                    phone_number=order_obj.shipping_address.phone_number,
                    full_name=order_obj.shipping_address.full_name,
                    address_line_1=order_obj.shipping_address.address_line_1,
                    address_line_2=order_obj.shipping_address.address_line_2,
                    postal_code=order_obj.shipping_address.postal_code,   
                )
            order_obj.final_address = order_address_obj
            order_obj.save()
            charge_obj = Charge.objects.new(order=order_obj, response=response)

            return redirect('carts:success')
        except KeyError:
            # 필수 값이 없을때 에러 처리
            print('response', response)
            messages.success(request, '필수 값이 없을때 에러 처리')
            return redirect('carts:fail')
        except Iamport.ResponseError as e:
            # 응답 에러 처리
            print('response', response)
            messages.success(request, '응답 에러 처리')
            return redirect('carts:fail')
        except Iamport.HttpError as http_error:
            # HTTP not 200 응답 에러 처리
            print('response', response)
            messages.success(request, 'HTTP not 200 응답 에러 처리')
            return redirect('carts:fail')

#         if is_paid:
#             # DB에 결제 정보 저장
#             # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
#             # if status == 'ready':
#             #     # DB에 가상계좌 발급정보 저장
#             #     print("결재 상태 : ready, vbankIssued")
#             #     return HttpResponse(json.dumps({'status': "vbankIssued", 'message': "가상계좌 발급 성공"}),
#             #                         content_type="application/json")
#             if status=='paid':
#                 print("결재 상태 : paid, success")

#                 order_obj.mark_paid()
#                 request.session['cart_items'] = 0
#                 del request.session['cart_id']
                
#                 # 사용포인트 차감
#                 if order_obj.point_total > 0:
#                     point_use = (-1) * order_obj.point_total
#                     point_details = "주문번호 {} 구매를 위한 포인트 {} 사용".format(order_obj, point_use)
#                     point_obj = Point.objects.new(user=user, amount=point_use, details=point_details)


#                 # 재고 있는것들에 대해서 아래와 같이 구매한다.
#                 for cart_item_obj in cart_obj.cart_items.all():
#                     if cart_item_obj.product_type == 'normal':
#                         if cart_item_obj.option is not None:
#                             option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
#                             option_obj.amount = option_obj.amount - cart_item_obj.amount
#                             option_obj.save()
#                             print('{}의 {}옵션이 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, option_obj.option, option_obj.amount))                 
#                         else:
#                             cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - cart_item_obj.amount
#                             cart_item_obj.product_item.save()
#                             print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))
                
#                 # 최종 주소 저장 및 charge 만들기
#                 order_address_obj = OrderAddress.objects.create(
#                     user=user,
#                     email=order_obj.shipping_address.email,
#                     phone_number=order_obj.shipping_address.phone_number,
#                     full_name=order_obj.shipping_address.full_name,
#                     address_line_1=order_obj.shipping_address.address_line_1,
#                     address_line_2=order_obj.shipping_address.address_line_2,
#                     postal_code=order_obj.shipping_address.postal_code,   
#                 )
#                 order_obj.final_address = order_address_obj
#                 order_obj.cart_items_name = cart_items_name
#                 order_obj.save()
#                 charge_obj = Charge.objects.new(order=order_obj, response=response)
#                 # print(response)
#                 order_complete_mail(user.email, order_obj)
#                 alimtalk_message = '''{user}님이 구매하신 상품의 결제가 완료되었습니다.

# 물품: {cart_items_name}
# 총 금액: {checkout_total}
# '''.format(user=user, cart_items_name=cart_items_name_iamport, checkout_total=order_obj.checkout_total)
#                 send(templateCode='alim3', to=user.phone_number, message=alimtalk_message)
#                 print("{}으로 결제완료 알림톡이 보내졌습니다.".format(user.phone_number))
#                 return redirect('carts:success')
#             else:
#                 print("결재 상태 : 결제가 실패하였습니다.")
#                 return redirect('carts:home')
#                 # return HttpResponse(json.dumps({'status': "fail", 'message': "결제 실패"}), content_type="application/json")
#         else:
#             print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
#             return redirect('carts:home')
####################################################################################################################








        # print('Ajax requested', post_purpose)
        # get_data = request.POST.get('get_data')
        # print(380, "get_data",get_data)
        # imp_uid = request.POST.get('imp_uid')
        # data = {
        #     "imp_key": IMPORT_REST_API_KEY,
        #     "imp_secret": IMPORT_REST_API_SECRET
        # }
        # print(data)
        # response = requests.post('https://api.iamport.kr/users/getToken', data=data)
        # data = response.json()
        # print(data)
        # my_token = data['response']['access_token']
        # print('my_token',my_token)

        # #  // imp_uid로 아임포트 서버에서 결제 정보 조회
        # headers = {"Authorization": my_token}
        # print("imp_uid", imp_uid)
        # print('data',data)
        # print('headers', headers)
        # response = requests.get('https://api.iamport.kr/payments/'+imp_uid, data=data, headers = headers)
        # data = response.json()

        # # // DB에서 결제되어야 하는 금액 조회 const
        # order_amount = order_obj.checkout_total
        # amountToBePaid = data['response']['amount']  # 아임포트에서 결제후 실제 결제라고 인지 된 금액
        # print('amountToBePaid',amountToBePaid)
        # status = data['response']['status']  # 아임포트에서의 상태
        # print('status',status)

        # if order_amount==amountToBePaid:
        #     # DB에 결제 정보 저장
        #     # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
        #     if status == 'ready':
        #         # DB에 가상계좌 발급정보 저장
        #         print("결재 상태 : ready, vbankIssued")
        #         return HttpResponse(json.dumps({'status': "vbankIssued", 'message': "가상계좌 발급 성공"}),
        #                             content_type="application/json")
        #     elif status=='paid':
        #         print("결재 상태 : paid, success")

        #         order_obj.mark_paid()
        #         request.session['cart_items'] = 0
        #         del request.session['cart_id']
                
        #         # 사용포인트 차감
        #         if order_obj.point_total > 0:
        #             point_use = (-1) * order_obj.point_total
        #             point_details = "주문번호 {} 구매를 위한 포인트 {} 사용".format(order_obj, point_use)
        #             point_obj = Point.objects.new(user=user, amount=point_use, details=point_details)


        #         # 재고 있는것들에 대해서 아래와 같이 구매한다.
        #         for cart_item_obj in cart_obj.cart_items.all():
        #             if cart_item_obj.product_type == 'normal':
        #                 if cart_item_obj.option is not None:
        #                     option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
        #                     option_obj.amount = option_obj.amount - cart_item_obj.amount
        #                     option_obj.save()
        #                     print('{}의 {}옵션이 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, option_obj.option, option_obj.amount))                 
        #                 else:
        #                     cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - cart_item_obj.amount
        #                     cart_item_obj.product_item.save()
        #                     print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))
                
        #         # 최종 주소 저장 및 charge 만들기
        #         order_address_obj = OrderAddress.objects.create(
        #             user=user,
        #             email=order_obj.shipping_address.email,
        #             phone_number=order_obj.shipping_address.phone_number,
        #             full_name=order_obj.shipping_address.full_name,
        #             address_line_1=order_obj.shipping_address.address_line_1,
        #             address_line_2=order_obj.shipping_address.address_line_2,
        #             postal_code=order_obj.shipping_address.postal_code,   
        #         )
        #         order_obj.final_address = order_address_obj
        #         order_obj.save()
        #         charge_obj = Charge.objects.new(order=order_obj, response=data['response'])

        #         return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
        #                             content_type="application/json")
        #     else:
        #         print("결재 상태 : 결제가 실패하였습니다.")
        #         return HttpResponse(json.dumps({'status': "fail", 'message': "결제 실패"}), content_type="application/json")
        # else:
        #     print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
        #     return HttpResponse(json.dumps({'status': "forgery", 'message': "위조된 결제시도"}), content_type="application/json") 
    
    # 모바일 checkout suceess 후 redirectino 일때...
    elif request.method == 'GET' and not checkout_directly :
        print('체크아웃 모바일결제 로딩')
        imp_uid = request.GET.get('imp_uid', None)
        response = iamport.find(imp_uid=imp_uid)
        merchant_uid = response['merchant_uid']
        order_amount = order_obj.checkout_total
        is_paid = iamport.is_paid(order_amount, merchant_uid=merchant_uid)
        status = response['status']
        
        
        print("모바일 Checkout requested")
        
        # imp_uid = request.GET.get('imp_uid')
        # merchant_uid = request.GET.get('merchant_uid')
        # imp_success = request.GET.get('imp_success')
        # print('imp_uid', imp_uid)
        # print('merchant_uid', merchant_uid)
        # print('imp_success', imp_success)
        
        # data = {
        #     "imp_key": IMPORT_REST_API_KEY,
        #     "imp_secret": IMPORT_REST_API_SECRET
        # }
        # print(data)
        # response = requests.post('https://api.iamport.kr/users/getToken', data=data)
        # data = response.json()
        # print(data)
        # my_token = data['response']['access_token']
        # print('my_token',my_token)
        # #  // imp_uid로 아임포트 서버에서 결제 정보 조회
        # headers = {"Authorization": my_token}
        # print("imp_uid", imp_uid)
        # print('data',data)
        # print('headers', headers)
        # response = requests.get('https://api.iamport.kr/payments/'+imp_uid, data=data, headers = headers)
        # data = response.json()
        # # // DB에서 결제되어야 하는 금액 조회 const
        # order_amount = order_obj.checkout_total
        # amountToBePaid = data['response']['amount']  # 아임포트에서 결제후 실제 결제라고 인지 된 금액

        # # response = requests.get('https://api.iamport.kr/payments/find'+merchant_uid)

        # # data = response.json()
        # # # // DB에서 결제되어야 하는 금액 조회 const
        # # order_amount = order_obj.checkout_total
        # # amountToBePaid = data['response']['amount']  # 아임포트에서 결제후 실제 결제라고 인지 된 금액
        # print('amountToBePaid',amountToBePaid)

        # status = data['response']['status']
        # print('status',status)


        if is_paid:
            # DB에 결제 정보 저장
            # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
            if status == 'ready':# and imp_success == 'true':
                # DB에 가상계좌 발급정보 저장
                print("결재 상태 : ready, vbankIssued")
                return redirect('carts:vbank')
            elif status=='paid':# and imp_success == 'true':
                print("결재 상태 : paid, success")

                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']

                # 사용포인트 차감
                if order_obj.point_total > 0:
                    point_use = (-1) * order_obj.point_total
                    point_obj = Point.objects.new(user=user, amount=point_use, details=point_details)


                # 재고 있는것들에 대해서 아래와 같이 구매한다.
                for cart_item_obj in cart_obj.cart_items.all():
                    if cart_item_obj.option is not None:
                        option_obj = SizeOption.objects.get(product_item=cart_item_obj.product_item, option=cart_item_obj.option)
                        option_obj.amount = option_obj.amount - cart_item_obj.amount
                        option_obj.save()
                        print('{}의 {}옵션이 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, option_obj.option, option_obj.amount))                 
                    else:
                        cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - cart_item_obj.amount
                        cart_item_obj.product_item.save()
                        print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))

                order_address_obj = OrderAddress.objects.create(
                    user=user,
                    email=order_obj.shipping_address.email,
                    phone_number=order_obj.shipping_address.phone_number,
                    full_name=order_obj.shipping_address.full_name,
                    address_line_1=order_obj.shipping_address.address_line_1,
                    address_line_2=order_obj.shipping_address.address_line_2,
                    postal_code=order_obj.shipping_address.postal_code,   
                )
                order_obj.final_address = order_address_obj
                order_obj.cart_items_name = cart_items_name
                order_obj.save()
                charge_obj = Charge.objects.new(order=order_obj, response=response)
                order_complete_mail(user.email, order_obj)
                alimtalk_message = '''{user}님이 구매하신 상품의 결제가 완료되었습니다.

물품: {cart_items_name}
총 금액: {checkout_total}
'''.format(user=user, cart_items_name=cart_items_name_iamport, checkout_total=order_obj.checkout_total)
                send(templateCode='alim3', to=user.phone_number, message=alimtalk_message)
                print("{}으로 결제완료 알림톡이 보내졌습니다.".format(user.phone_number))
                # return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}), content_type="application/json")
                return redirect('carts:success')

            elif status=='failed':# or imp_success == 'false':
                print("결재 상태 : 결제가 실패하였습니다.")
                return redirect('carts:fail')
        else:
            print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
            return redirect('carts:fail')

    elif request.method == 'POST' and not post_purpose and not request.is_ajax() or checkout_directly:
        print('체크아웃 최초화면 로딩')
        print('context', context)

        # 바로구매의 get으로 인한 http404 방지용
        # 결제가 됐을때는 아래의 session이 없어져도 상관없다. 
        # 하지만 결제가 안됐을때 checkout_iamport는 get으로 오게되어 모바일결제로 넘어오게 된다. 
        # 이것을 방지하기 위해 아래와 같이 다시 session을 만들어 첫화면이 보이게 해준다.
        request.session['checkout_iamport_now'] = True
        return render(request, "carts/checkout-iamport.html", context)

# billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
# email           = models.EmailField(max_length=255, unique=True)
# phone_number    = models.CharField(max_length=255, blank=True, null=True)
# full_name       = models.CharField(max_length=255, blank=True, null=True)

# address_type    = models.CharField(max_length=120, choices=ADDRESS_TYPES)
# address_line_1  = models.CharField(max_length=120)
# address_line_1  = models.CharField(max_length=120)
# address_line_2  = models.CharField(max_length=120, null=True, blank=True)
# postal_code     = models.CharField(max_length=120)
# timestamp       = models.DateTimeField(auto_now_add=True)



    #     shipping_address_qs = Address.objects.filter(billing_profile__email=user.email, address_type='shipping')
    #     if shipping_address_qs.count() == 1:
    #         shipping_address_obj = shipping_address_qs.first()
    #     else:
    #         print('address에 문제가 있다.')
    #     address = shipping_address_obj.get_address()
    #     postcode = shipping_address_obj.get_postal_code()
        
    #     cart_items_name = ""
    #     for cart_item in cart_obj.cart_items.all():
    #         if cart_item.product_type == 'ticket':
    #             cart_items_name = cart_items_name + "ticket_" + str(cart_item.ticket_item.tickets_type) + "_"
    #         else:
    #             cart_items_name = cart_items_name + cart_item.product_item.product.title + "_"
        
    #     iamport_data = {
    #                 'pg': "html5_inicis.INIpayTest",
    #                 'pay_method':'card',
    #                 'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
    #                 'name':cart_items_name,
    #                 'amount': int(order_obj.total),
    #                 'buyer_email': billing_profile.email,
    #                 'buyer_name': user.full_name,
    #                 'buyer_tel': user.phone_number,# 얘는 만들어야함. 
    #                 'buyer_addr': address,
    #                 'buyer_postcode': postcode
    #                 }
    #         # checkout 버튼 눌렸을때 
    #     if request.is_ajax():
    #         get_data = request.POST.get('get_data')
    #         print(380, "get_data",get_data)
    #         # if not get_data:
    #         #     # imaport_data 가져오기 버튼 누름.
    #         #     return JsonResponse(iamport_data)
    #         # else:
    #         #     print(385, ' elif not get_data',get_data)
    #         # 결재정보 확인 실행
    #         imp_uid = request.POST.get('imp_uid')
    #         # // 액세스 토큰(access token) 발급받기
    #         data = {
    #             "imp_key": IMPORT_REST_API_KEY,
    #             "imp_secret": IMPORT_REST_API_SECRET
    #         }
    #         print(data)
    #         response = requests.post('https://api.iamport.kr/users/getToken', data=data)
    #         data = response.json()
    #         print(data)
    #         my_token = data['response']['access_token']
    #         print('my_token',my_token)
    #         #  // imp_uid로 아임포트 서버에서 결제 정보 조회
    #         headers = {"Authorization": my_token}
    #         print("imp_uid", imp_uid)
    #         print('data',data)
    #         print('headers', headers)
    #         response = requests.get('https://api.iamport.kr/payments/'+imp_uid, data=data, headers = headers)
    #         data = response.json()
    #         # // DB에서 결제되어야 하는 금액 조회 const
    #         order_amount = order_obj.checkout_total
    #         amountToBePaid = data['response']['amount']  # 아임포트에서 결제후 실제 결제라고 인지 된 금액
    #         print('amountToBePaid',amountToBePaid)
    #         status = data['response']['status']  # 아임포트에서의 상태
    #         print('status',status)
    #         if order_amount==amountToBePaid:
    #             # DB에 결제 정보 저장
    #             # await Orders.findByIdAndUpdate(merchant_uid, { $set: paymentData}); // DB에
    #             if status == 'ready':
    #                 # DB에 가상계좌 발급정보 저장
    #                 print("결재 상태 : ready, vbankIssued")
    #                 return HttpResponse(json.dumps({'status': "vbankIssued", 'message': "가상계좌 발급 성공"}),
    #                                     content_type="application/json")
    #             elif status=='paid':
    #                 print("결재 상태 : paid, success")

    #                 order_obj.mark_paid()
    #                 request.session['cart_items'] = 0
    #                 del request.session['cart_id']
                    
    #                 # 사용포인트 차감
    #                 if order_obj.point_total > 0:
    #                     point_use = (-1) * order_obj.point_total
    #                     point_obj = Point.objects.new(user=user, amount=point_use, details=point_details)


    #                 # 재고 있는것들에 대해서 아래와 같이 구매한다.
    #                 for cart_item_obj in cart_obj.cart_items.all():
    #                     if cart_item_obj.product_type == 'normal':
    #                         cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - 1
    #                         cart_item_obj.product_item.save()
    #                         print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))
                    

    #                 return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
    #                                     content_type="application/json")
    #             else:
    #                 pass
    #         else:
    #             print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
    #             return HttpResponse(json.dumps({'status': "forgery", 'message': "위조된 결제시도"}), content_type="application/json")
            
    #     else:
    #         post_purpose = request.POST.get('post_purpose')

    #         if post_purpose == 'use_point':
    #             use_point = request.POST.get('use_point')
    #             try:
    #                 order_obj.point_total = int(use_point)
    #                 order_obj.checkout_total = order_obj.total - int(use_point)
    #                 order_obj.save()
    #                 redirect("carts:checkout-iamport")
    #             except:
    #                 messages.error(request, "사용하려는 POINT를 다시 입력해주세요.")
    #                 redirect("carts:checkout-iamport")
    #         elif post_purpose == 'checkout_0':
    #             order_obj.mark_paid()
    #             request.session['cart_items'] = 0
    #             del request.session['cart_id']
                
    #             # 사용포인트 차감
    #             if order_obj.point_total > 0:
    #                 point_use = (-1) * order_obj.point_total
    #                 point_obj = Point.objects.new(user=user, amount=order_obj.point_total, details=point_details)
                
    #             # 재고 있는것들에 대해서 아래와 같이 구매한다.
    #             for cart_item_obj in cart_obj.cart_items.all():
    #                 if cart_item_obj.product_type == 'normal':
    #                     cart_item_obj.product_item.amount = cart_item_obj.product_item.amount - 1
    #                     cart_item_obj.product_item.save()
    #                     print('{}가 checkout 되었습니다. 현재고는 {}개입니다.'.format(cart_item_obj.product_item.product.title, cart_item_obj.product_item.amount))                 
    #             return render(request, 'carts/checkout-done.html', {}) # 
        
    
        
    #     # if order_obj.total >= user.points:

    
    # context = {
    #     'object':order_obj,
    #     'billing_profile': billing_profile,
    #     # 'login_form': login_form,
    #     # 'guest_form': guest_form,
    #     # 'address_form': address_form,
    #     'address_qs': address_qs,
    #     'has_card': has_card,
    #     'publish_key': STRIPE_PUB_KEY,
    #     # 결재용 context
    #     'pg': "html5_inicis.INIpayTest",
    #     'pay_method':'card',
    #     'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
    #     'name':cart_items_name,
    #     'amount': order_obj.checkout_total,
    #     'buyer_email': billing_profile.email,
    #     'buyer_name': user.full_name,
    #     'buyer_tel': user.phone_number,# 얘는 만들어야함. 
    #     'buyer_addr': address,
    #     'buyer_postcode': postcode,
    #     'point_available': point_available
    #     }
    
    
    # return render(request, "carts/checkout-iamport.html", context)

    
class CheckoutView(generic.TemplateView):
    template_name='carts/payment_test.html'
    

@login_required
def payment_complete(request):
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

@login_required
def payment_fail(request):
    return render(request, 'carts/payment_fail.html', {})

@login_required
def payment_success(request):
    return render(request, 'carts/payment_success.html', {})




# 체크아웃완료되면 이메일 보내기.
def order_complete_mail(email, order):
    base_url = getattr(settings, 'BASE_URL', 'https://moum8.com')
    key_path = reverse("home") # use reverse
    path = "{base}".format(base=base_url)
    
    
    context = {
        'path':path,
        'email': email,
        'order_id': order.order_id,
        'full_name': order.final_address.full_name,
        'phone_number': order.final_address.phone_number,
        'address': order.final_address.get_address,
        'cart_items_name': order.cart_items_name,
        'total': order.total, # 물건값
        'shiping_cost': order.shipping_cost,
        'point_total': order.point_total,
        'checkout_total': order.checkout_total,
        'customer_request': order.customer_request,
        'shipping_count': order.shipping_count,

    }
    txt_ = get_template("orders/emails/order_complete_email.txt").render(context)
    html_ = get_template("orders/emails/order_complete_email.html").render(context)
    subject = '명품 병행수입 쇼핑몰_MOUM8_상품결제 완료 메일'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # send_mail = send_email(
    #                         emailMsg=txt_, 
    #                         to=self.email, 
    #                         subject=subject)
    sent_mail = send_mail(
                subject,
                txt_,
                from_email,
                recipient_list,
                html_message=html_,
                fail_silently=False,
                )
    print("{}님께 결제완료 이메일이 보내졌습니다.".format(order.billing_profile.user))
    return send_mail