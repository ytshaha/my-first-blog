import requests
import json
from django.http import HttpResponse
from django.http import Http404


from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib import messages


from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order #, TicketOrder

from .models import TicketItem, Ticket
from points.models import Point
from .forms import TicketItemForm
from mysite.utils import random_string_generator

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0")

stripe.api_key = STRIPE_SECRET_KEY

from mysite.client import Iamport


TICKET_BUY_INFO = [
                { "amount": 1, "subtotal": 5000, "total": 5000, 'sale_ratio': 0},
                { "amount": 3, "subtotal": 15000, "total": 14250, 'sale_ratio': 5},
                { "amount": 5, "subtotal": 25000, "total": 23750, 'sale_ratio': 5},
                { "amount": 10, "subtotal": 50000, "total": 45000, 'sale_ratio': 10},
                { "amount": 20, "subtotal": 100000, "total": 90000, 'sale_ratio': 10},
                { "amount": 30, "subtotal": 150000, "total": 135000, 'sale_ratio': 10}
                ]

IAMPORT_CODE = getattr(settings, "IAMPORT_CODE", 'imp30832141')
IMPORT_REST_API_KEY = getattr(settings, "IMPORT_REST_API_KEY", '8306112827056798')
IMPORT_REST_API_SECRET = getattr(settings, "IMPORT_REST_API_SECRET", 'WmAHFCAyZFfaMy10g6xRPvFawuuJAVPxiqfY2Pw2uMcgkegAlOsak7kQCOzdKpK2PZ0RPxTjj6AEkQfF')


# class TicketAvailableListView(generic.ListView):
#     template_name = 'tickets/ticket_home.html'
#     context_object_name = 'tickets'
    
#     def get_queryset(self):
#         request = self.request
#         try:
#             tickets = Ticket.objects.get(request)
#         except Ticket.DoesNotExist:
#             return HttpResponse({"messsage":"You have not Available ticket now. Buy some ticket."})

#         print(tickets)
#         if tickets.exists():
#             return tickets
        # else:
        #     return HttpResponse({"messsage":"You have not Available ticket now. Buy some ticket."})
@login_required
def ticket_home(request):
    # 로긴했을때 아래 과정들에 대한 체크가 필요할 듯.
    # 현재 사용중이면 request.session['ticket_activate'] = True
    # 하루지나서 이제 못사용 하면 False
    
    # 일단 POST가 아닐떄
    # print(request.session['ticket_activate'])
    try:
        tickets = Ticket.objects.get(request)
    except Ticket.DoesNotExist:
        return HttpResponse({"messsage":"You have not Available ticket now. Buy some ticket."})
    print(request.POST)
    
    # 활성화 티켓 존재여부
    activated = False
    if Ticket.objects.filter(user=request.user, status='activate').exists():
        activated = True


    if request.method == "POST":
        post_purpose = request.POST.get('post_purpose')

        ticket_id = request.POST.get('ticket_id')
        if ticket_id is not None:
            try:
                ticket_qs = Ticket.objects.filter(ticket_id=ticket_id)
            except Ticket.DoesNotExist:
                print("What's happening? Is ticket gone?")
                return redirect("tickets:home")
        # 티켓활성화 POST일때
        if post_purpose == "activate_ticket":
            # ticket_id = request.POST.get('ticket_id')
            # if ticket_id is not None:
            #     try:
            #         ticket_obj = Ticket.objects.filter(ticket_id=ticket_id)
            #     except Ticket.DoesNotExist:
            #         print("What's happening? Is ticket gone?")
            #         return redirect("tickets:home")
                # 이미 사용하고 있는 티켓이 있으면 에러메세지로 이미 사용중인 티켓이 있습니다라고 띄운다.
            if activated:
                messages.success(request, "이미 사용중인 티켓이 있습니다.")
                context = {
                    'activated': activated,
                    'tickets':tickets
                }
                return render(request, "tickets/ticket_home.html", context)
            if ticket_qs.count() == 1:
                ticket_obj = ticket_qs.first()
                ticket_obj.timestamp = datetime.datetime.now()
                ticket_obj.status = 'activate'
                ticket_obj.save()
                request.session['ticket_activate'] = True
                    # request.user.active = True # 이건 나중에 사용자단에서 그냥 비딩가능하게 하기위함. 
                return redirect("tickets:home")
        # 포인트전환 POST일때
        elif post_purpose == "trasnfer_point":
            if ticket_qs.count() == 1:
                ticket_obj = ticket_qs.first()
                if ticket_obj.transfer_point == True:
                    messages.success(request, "티켓({})은 이미 포인트로 전환되었습니다.".format(ticket_obj.ticket_id))
                    return redirect("tickets:home")
                ticket_obj.transfer_point = True
                ticket_obj.save()
                point_details = "경매 미당첨된 티켓({})의 포인트 5000점 전환".format(ticket_obj.ticket_id)
                point_obj = Point.objects.new(user=request.user, amount=5000, details=point_details)
                messages.success(request, "티켓({})이 {}님의 포인트 5000점으로 전환되었습니다.".format(request.user, ticket_obj.ticket_id))
                return redirect("tickets:home")
    
    context = {
                    'activated': activated,
                    'tickets':tickets
                }
    # POST도 아닐때의 최종 return
    return render(request, "tickets/ticket_home.html", context)


# 티켓 구매 페이지. 일단 FBV로 만든다.
@login_required
def ticket_buy(request):
    print(request.POST)
    if request.method == 'POST':
        form = TicketItemForm(request.POST)
        print("form",form)
        print("form.is_valid()",form.is_valid())
        if form.is_valid():
            ticket_item = form.save(commit=False)
            ticket_item.user = request.user
            ticket_item.save()
            request.session['ticket_item_id'] = ticket_item.id
            request.session['product_type'] = 'ticket'
            
            return redirect('carts:update')
    else:
        form = TicketItemForm()
        # ticket_type_list = [1,3,5,10,20,30]
        # ticket_subtotal_list = [5000,15000,25000,50000,100000,150000]
        # ticket_total_list = [5000,14250,23750,45000,90000,135000]
        # ticket_info = zip(ticket_type_list, ticket_subtotal_list, ticket_total_list)
        
        context = {
            'form':form,
            'ticket_buy_info': TICKET_BUY_INFO
        }
        return render(request, 'tickets/ticket_buy.html', context)



# @login_required
# def ticket_cart_home(request):
#     ticketcart_obj, new_obj = TicketCart.objects.new_or_get(request)
#     return render(request, "tickets/ticket_cart_home.html", {'ticketcart_obj':ticketcart_obj})

# @login_required
# def ticket_checkout_home(request):
#     ticketcart_obj, ticketcart_created = TicketCart.objects.new_or_get(request)
#     order_obj = None
#     if ticketcart_created:
#         return redirect("tickets:buy")   
    
#     login_form = LoginForm(request=request)
#     guest_form = GuestForm(request=request)
#     address_form = AddressForm()
#     billing_address_id = request.session.get('billing_address_id', None)
#     shipping_address_id = request.session.get('shipping_address_id', None)

#     billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
#     address_qs = None
#     has_card = False
#     is_ticket = True
#     request.session['is_ticket'] = is_ticket
#     if billing_profile is not None:
#         if request.user.is_authenticated:
#             address_qs = Address.objects.filter(billing_profile=billing_profile)
#         order_obj, order_obj_created = TicketOrder.objects.new_or_get(billing_profile, ticketcart_obj)
#         if shipping_address_id:
#             order_obj.shipping_address = Address.objects.get(id=shipping_address_id) 
#             del request.session['shipping_address_id']
#         if billing_address_id:
#             order_obj.billing_address = Address.objects.get(id=billing_address_id)
#             del request.session['billing_address_id']
#         if billing_address_id or shipping_address_id:
#             order_obj.save()
#         has_card = billing_profile.has_card
    
#     # if request.method == "POST":
#     #     "check that order is done"
#     #     is_prepared = order_obj.check_done()
#     #     if is_prepared:
#     #         did_charge, charge_msg = billing_profile.charge(order_obj)
#     #         if did_charge:
#     #             order_obj.mark_paid()
#     #             # request.session['cart_items'] = 0 # 왜하는지 모르겠네.--->???
#     #             del request.session['ticketcart_id']
#     #             if not billing_profile.user:
#     #                 billing_profile.set_cards_inactive()
#     #             request.session['order_id'] = order_obj.id
#     #             return redirect("tickets:success")
#     #         else:
#     #             print(charge_msg)
#     #             return redirect("tickets:checkout")

#     # context = {
#     #     'object':order_obj,
#     #     'billing_profile': billing_profile,
#     #     'login_form': login_form,
#     #     'guest_form': guest_form,
#     #     'address_form': address_form,
#     #     'address_qs': address_qs,
#     #     'has_card': has_card,
#     #     'publish_key': STRIPE_PUB_KEY,
#     #     'is_ticket': is_ticket
#     # }
#     # print(180, 'context',context)
#     # return render(request, "tickets/checkout.html", context)



#     # 아임포트 토큰 가져오기
#     iamport = Iamport(imp_key=IMPORT_REST_API_KEY, imp_secret=IMPORT_REST_API_SECRET)
#     # access_token = iamport._get_token()
#     # response = iamport.get_response(access_token)
#     # 결재정보 받아오기위한 json data 준비
#     user = request.user

#     shipping_address_qs = Address.objects.filter(billing_profile__email=user.email, address_type='shipping')
#     if shipping_address_qs.count() == 1:
#         shipping_address_obj = shipping_address_qs.first()
#     else:
#         print('address에 문제가 있다.')
#     address = shipping_address_obj.get_address()
#     postcode = shipping_address_obj.get_postal_code()
    
#     cart_items_name = "경매 참여 티켓 {}장".format(ticketcart_obj.tickets_type)

#     iamport_data = {
#                 'pg': "html5_inicis",
#                 'pay_method':'card',
#                 'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
#                 'name':cart_items_name,
#                 'amount': order_obj.total,
#                 'buyer_email': billing_profile.email,
#                 'buyer_name': user.full_name,
#                 'buyer_tel': user.phone_number,# 얘는 만들어야함. 
#                 'buyer_addr': address,
#                 'buyer_postcode': postcode
#                 }
#     if request.method == 'POST' and request.is_ajax():
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
#         response = requests.get('https://api.iamport.kr/payments/'+imp_uid, data=data, headers = headers)
#         data = response.json()
#         # // DB에서 결제되어야 하는 금액 조회 const
#         order_amount = order_obj.total
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
#                 # request.session['cart_items'] = 0
#                 del request.session['ticketcart_id']
#                 request.session['order_id'] = order_obj.id

#                 return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
#                                     content_type="application/json")
#             else:
#                 pass
#         else:
#             print("결재 상태 : forgery, 결재금액과 상품금액이 다릅니다.")
#             return HttpResponse(json.dumps({'status': "forgery", 'message': "위조된 결제시도"}), content_type="application/json")

#     context = {
#         'object':order_obj,
#         'billing_profile': billing_profile,
#         'login_form': login_form,
#         'guest_form': guest_form,
#         'address_form': address_form,
#         'address_qs': address_qs,
#         'has_card': has_card,
#         'publish_key': STRIPE_PUB_KEY,
#         # 결재용 context
#         'pg': "html5_inicis",
#         'pay_method':'card',
#         'merchant_uid':order_obj.order_id + "_" + random_string_generator(size=10),
#         'name':cart_items_name,
#         'amount': order_obj.total,
#         'buyer_email': billing_profile.email,
#         'buyer_name': user.full_name,
#         'buyer_tel': user.phone_number,# 얘는 만들어야함. 
#         'buyer_addr': address,
#         'buyer_postcode': postcode
#         # 'pg' : 'html5_inicis', 
#         # 'pay_method' : 'card',
#         # 'merchant_uid' : 'merchant_' + random_string_generator(size=10),
#         # 'name' : '주문명:결제테스트',
#         # 'amount' : 100,
#         # 'buyer_email' : 'iamport@siot.do',
#         # 'buyer_name' : '고길동',
#         # 'buyer_tel' : '010-1234-5678',
#         # 'buyer_addr' : '서울특별시 영등포구 도신로',
#         # 'buyer_postcode' : '123-456',

#                 }
    
#     # print('♥♥♥♥♥context')
#     # print(context)
    
#     return render(request, "tickets/checkout-iamport.html", context)




# @login_required
# def checkout_done_view(request):
#     order_id = request.session.get('order_id')
#     print(order_id)
#     try:
#         order_obj = TicketOrder.objects.get(id=order_id)
#     except TicketOrder.DoesNotExist:
#         messages.success(request, "티켓이 정상적으로 구매되지 않았습니다..")
#         return render(request, "tickets/checkout-done.html", {'msg': '티켓이 정상적으로 구매되지 않았습니다..'})    
#     ticket_count = order_obj.ticketcart.tickets_type
#     if request.user.is_authenticated:
#         user = request.user
#         if order_obj.status == 'paid':
#             for i in range(ticket_count):
#                 ticket_obj = Ticket.objects.new(user=user)
#                 ticket_obj.save()
#     try:
#         tickets = Ticket.objects.get(request)
#     except Ticket.DoesNotExist:
#         return HttpResponse({"messsage":"You have not Available ticket now. Buy some ticket."})

#     return render(request, "tickets/checkout-done.html", {'msg': 'Thank you for your order!!', 'tickets':tickets})




# # def ticket_buy_remove(request):
# #     ticketcart_id = request.POST.get('ticketcart_id')
    
# #     if ticketcart_id is not None:
# #         try:
# #             ticketcart_id = TicketCart.objects.get(id=ticketcart_id)
# #         except TicketCart.DoesNotExist:
# #             print("Show message to user, ticketcart is gone?")
# #             return redirect("tickets:home")
# #         ticketcart_obj, new_obj = TicketCart.objects.new_or_get(request)
# #         if ticketcart_obj.exists():
# #             ticketcart_obj.delete()
# #             return redirect("tickets:home")
# #         if request.is_ajax(): # Asyncronous JavaScripts ANd XM
# #             print("Ajax request")
# #             json_data = {
# #                 'removed':not added,
# #                 "cartItemCount": cart_obj.products.count()
# #             }
# #             return JsonResponse(json_data, status=200)
# #             # return JsonResponse({"message":"Error 400"}, status_code=400) # django rest framework

# #     return redirect("carts:home")