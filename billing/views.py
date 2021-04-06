import requests
import json

from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from mysite.client import Iamport
from django.contrib import messages

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import BillingProfile, Card

IAMPORT_CODE = getattr(settings, "IAMPORT_CODE", 'imp30832141')
IMPORT_REST_API_KEY = getattr(settings, "IMPORT_REST_API_KEY", '8306112827056798')
IMPORT_REST_API_SECRET = getattr(settings, "IMPORT_REST_API_SECRET", 'WmAHFCAyZFfaMy10g6xRPvFawuuJAVPxiqfY2Pw2uMcgkegAlOsak7kQCOzdKpK2PZ0RPxTjj6AEkQfF')


def payment_method_view(request):
    # if request.user.is_authenticated:
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.customer_id
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
        
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key":STRIPE_PUB_KEY, "next_url":next_url})

def payment_method_createview(request):
    if request.method == "POST" and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"messsage":"Cannot find this user"}, status_code=401)
        token = request.POST.get("token")
        if token is not None:
            new_card_obj = Card.objects.add_new(billing_profile=billing_profile, token=token)
        return JsonResponse({"message":"Success! Your card was added."})
    return HttpResponse("error", status_code=401)



class CardHomeListView(LoginRequiredMixin, generic.ListView):
    '''
    카드가 있으면 카드 보여주고 없으면 간편결제용 카드 등록 버튼 하나 중간에 딱 놓기.
    '''
    template_name = 'billing/card_home.html'
    context_object_name = 'cards'

    def get_context_data(self, *args, **kwargs):
        context = super(CardHomeListView, self).get_context_data(*args, **kwargs)
        
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        user = request.user

        card_qs = Card.objects.filter(user=user).order_by('-timestamp')

        return card_qs

def card_register(request):
    user = request.user
    billing_profile_qs = BillingProfile.objects.filter(user=user)
    card_count = Card.objects.filter(user=user).count()
    customer_uid = "cid_{}_{}".format(user, card_count+1)
    print('customer_uid', customer_uid)


    context = {
        'pg': "html5_inicis.INIBillTst",
        'pay_method':'card',
        'merchant_uid':"issue_billingkey_monthly_0001",
        'customer_uid': customer_uid,
        'name':"최초인증결제",
        'amount': 0,
        'buyer_email': 'test@test.com',
        'buyer_name': 'test',
        'buyer_tel': '010-1234-5678',# 얘는 만들어야함. 
    }
    if request.method == 'POST' and request.is_ajax():
        card_name = request.POST.get('card_name', None)
        print('카드네임', card_name)
        iamport = Iamport(imp_key=IMPORT_REST_API_KEY, imp_secret=IMPORT_REST_API_SECRET)
        imp_uid = request.POST.get('imp_uid', None)
        response = iamport.find(imp_uid=imp_uid)
        print(response)
        status = response['status']
        
        if status=='paid':
            print("결재 상태 : paid, success")
            card_obj = Card.objects.create(
                                        user=user, 
                                        card_name=card_name, 
                                        customer_uid=customer_uid
                                        )
            card_obj.set_active()

            return HttpResponse(json.dumps({'status': "success", 'message': "일반 결제 성공"}),
                                content_type="application/json")
        else:
            print("결재 상태 : 결제가 실패하였습니다.")
            return HttpResponse(json.dumps({'status': "fail", 'message': "결제 실패"}), content_type="application/json")

    return render(request, 'billing/card_register.html', context)


def card_select(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id', None)
        if card_id is None:
            messages.success(reqeust, "카드를 선택해주세요.")
            return redirect('accounts:card_select')
        card_obj = Card.objects.get(id=card_id)
        card_obj.set_active()
        messages.success(request, '{} 카드가 간편 결제카드로 지정되었습니다.'.format(card_obj.card_name))
        return redirect('accounts:card_home')
    user = request.user
    card_qs = Card.objects.filter(user=user).order_by('-timestamp')
    context = {
        'cards':card_qs,
    }
    return render(request, 'billing/card_select.html', context)        

