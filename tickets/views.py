from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.conf import settings
from django.http import HttpResponse
import datetime

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order, TicketOrder

from .models import TicketCart, Ticket
from .forms import TicketCartForm

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0")

stripe.api_key = STRIPE_SECRET_KEY




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
    
    # 포스트일때
    if request.method == "POST":
        ticket_id = request.POST.get('ticket_id')
        if ticket_id is not None:
            try:
                ticket_obj = Ticket.objects.filter(ticket_id=ticket_id)
            except Ticket.DoesNotExist:
                print("What's happening? Is ticket gone?")
                return redirect("tickets:home")
            # 이미 사용하고 있는 티켓이 있으면 에러메세지로 이미 사용중인 티켓이 있습니다라고 띄운다.
            if Ticket.objects.filter(user=request.user, status='activate').exists():
                return render(request, "tickets/ticket_home.html", {'tickets':tickets, "message":"이미 사용중인 티켓이 있습니다."})
            ticket_obj = ticket_obj.first()
            ticket_obj.timestamp = datetime.datetime.now()
            ticket_obj.status = 'activate'
            ticket_obj.save()
            request.session['ticket_activate'] = True
            # request.user.active = True # 이건 나중에 사용자단에서 그냥 비딩가능하게 하기위함. 
        return redirect("tickets:home")
    
    # POST도 아닐때의 최종 return
    return render(request, "tickets/ticket_home.html", {'tickets':tickets})


# 티켓 구매 페이지. 일단 FBV로 만든다.
def ticket_buy(request):
    if request.method == 'POST':
        form = TicketCartForm(request.POST)
        if form.is_valid():
            ticketcart = form.save(commit=False)
            ticketcart.user = request.user
            ticketcart.save()
            request.session['ticketcart_id'] = ticketcart.id
            return redirect('tickets:cart')

    else:
        form = TicketCartForm()
        return render(request, 'tickets/ticket_buy.html', {'form':form})

def ticket_cart_home(request):
    ticketcart_obj, new_obj = TicketCart.objects.new_or_get(request)
    return render(request, "tickets/ticket_cart_home.html", {'ticketcart_obj':ticketcart_obj})

def ticket_checkout_home(request):
    ticketcart_obj, ticketcart_created = TicketCart.objects.new_or_get(request)
    order_obj = None
    if ticketcart_created:
        return redirect("tickets:buy")   
    
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    is_ticket = True
    request.session['is_ticket'] = True
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = TicketOrder.objects.new_or_get(billing_profile, ticketcart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id) 
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card

    if request.method == "POST":
        "check that order is done"
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, charge_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()
                # request.session['cart_items'] = 0 # 왜하는지 모르겠네.--->???
                del request.session['ticketcart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                request.session['order_id'] = order_obj.id
                return redirect("tickets:success")
            else:
                print(charge_msg)
                return redirect("tickets:checkout")

    context = {
        'object':order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        'has_card': has_card,
        'publish_key': STRIPE_PUB_KEY,
        'is_ticket': is_ticket
    }
    return render(request, "tickets/checkout.html", context)

def checkout_done_view(request):
    order_id = request.session.get('order_id')
    order_obj = TicketOrder.objects.get(id=order_id)
    ticket_count = order_obj.ticketcart.tickets_type
    if request.user.is_authenticated:
        user = request.user
        if order_obj.status == 'paid':
            for i in range(ticket_count):
                ticket_obj = Ticket.objects.new(user=user)
                ticket_obj.save()
    try:
        tickets = Ticket.objects.get(request)
    except Ticket.DoesNotExist:
        return HttpResponse({"messsage":"You have not Available ticket now. Buy some ticket."})
    return render(request, "tickets/checkout-done.html", {'tickets':tickets})




# def ticket_buy_remove(request):
#     ticketcart_id = request.POST.get('ticketcart_id')
    
#     if ticketcart_id is not None:
#         try:
#             ticketcart_id = TicketCart.objects.get(id=ticketcart_id)
#         except TicketCart.DoesNotExist:
#             print("Show message to user, ticketcart is gone?")
#             return redirect("tickets:home")
#         ticketcart_obj, new_obj = TicketCart.objects.new_or_get(request)
#         if ticketcart_obj.exists():
#             ticketcart_obj.delete()
#             return redirect("tickets:home")
#         if request.is_ajax(): # Asyncronous JavaScripts ANd XM
#             print("Ajax request")
#             json_data = {
#                 'removed':not added,
#                 "cartItemCount": cart_obj.products.count()
#             }
#             return JsonResponse(json_data, status=200)
#             # return JsonResponse({"message":"Error 400"}, status_code=400) # django rest framework

#     return redirect("carts:home")