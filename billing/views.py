from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import BillingProfile, Card

import stripe

STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0")

stripe.api_key = STRIPE_SECRET_KEY

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

