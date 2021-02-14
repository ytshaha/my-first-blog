from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

import stripe
stripe.api_key = "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM"
STRIPE_PUB_KEY = "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0"
  
def payment_method_view(request):
    return render(request, 'billing/payment-method.html', {"publish_key":STRIPE_PUB_KEY})

def payment_method_createview(request):
    print(request)
    if request.method == "POST" and request.is_ajax():
        print(request.POST)
        return JsonResponse({"message":"Done"})
    return HttpResponse("error", status_code=401)

