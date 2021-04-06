from datetime import datetime
import pytz

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save, pre_save

from accounts.models import GuestEmail
# from orders.models import OrderAddress


# import stripe
# STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM")
# stripe.api_key = STRIPE_SECRET_KEY
User = settings.AUTH_USER_MODEL
# Create your models here.
# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
class CardManager(models.Manager):
    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)

    # def add_new(self, billing_profile, token):
    #     if token:
    #         stripe_card_response = stripe.Customer.create_source(billing_profile.customer_id, source=token)
    #         new_card = self.model(
    #             billing_profile = billing_profile,
    #             stripe_id = stripe_card_response.id,
    #             brand = stripe_card_response.brand,
    #             country = stripe_card_response.country,
    #             exp_month = stripe_card_response.exp_month,
    #             exp_year = stripe_card_response.exp_year,
    #             last4 = stripe_card_response.last4
    #         )
    #         new_card.save()
    #         return new_card
    #     return None

class Card(models.Model):
    # pass
    user            = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    card_name       = models.CharField(default='abc', max_length=120)
    customer_uid    = models.CharField(default='abc', max_length=120)
    active          = models.BooleanField(default=False)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return "{} {}".format(self.user, self.card_name)

    def set_active(self):
        '''
        해당카드를 default로 사용하고 나머지카드는 deactive 시킴.(결제창에서 쓸 카드.)
        그래서 결제창에서 사용자 카드 설정 링크 버튼 추가해야할듯.
        '''
        # card_qs = Card.objects.filter(card_name=card_name)
        # if card_qs.count() == 1:
        #     card_obj = card_qs.first()
        #     card_obj.active = True
        #     card_obj.save()
        #     Card.objects.filter(user=self.request.user).exclude(card_name=card_name).update(active=False)
        #     return card_obj
        # else:
        #     print('{} 카드가 없습니다.'.format(card_name))
        #     return None
        self.active = True
        self.save()
        Card.objects.filter(user=self.user).exclude(id=self.id).update(active=False)
        return self
        



class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user    
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)

        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
            created = True
        else:
            pass
        return obj, created

class BillingProfile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email           = models.EmailField()

    full_name       = models.CharField(max_length=255, blank=True, null=True)
    phone_number    = models.CharField(max_length=255, blank=True, null=True)
    
    active          = models.BooleanField(default=True)
    update          = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    card            = models.ForeignKey(Card, null=True, blank=True, on_delete=models.CASCADE)
    
    objects = BillingProfileManager()

    def __str__(self):
        return self.email
    
    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        return self.card_set.all()

    def get_payment_method_url(self):
        return reverse("billing-payment-method")

    @property
    def has_card(self): # instance.has_card
        card_qs = self.get_cards()
        return card_qs.exists() # True or False

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()

# customer_id in Stripe or Braintree가 생기면 부활할겅다. 
# def billing_profile_created_receiver(sender, instance, *args, **kwargs):
#     if not instance.customer_id and instance.email:
#         print("ACTURE API REQUEST Send to stripe")
#         customer = stripe.Customer.create(
#             email = instance.email,
#         )
#         print(customer)
#         instance.customer_id = customer.id

# pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)



        

# class ChargeManager(models.Manager):
    # def do(self, billing_profile, order_obj, card=None): # Charge.objects.do()
    #     card_obj = card
    #     if card_obj is None:
    #         cards = billing_profile.card_set.filter(default=True) # card_obj.billing_profile
    #         if cards.exists():
    #             card_obj = cards.first()
    #     if card_obj is None:
    #         return False, "No cards available."

    #     c = stripe.Charge.create(
    #         amount = int(order_obj.total * 100), # 39.19 -->3919
    #         currency = "usd",
    #         customer = billing_profile.customer_id,
    #         source = card_obj.stripe_id,
    #         metadata = {"order_id": order_obj.order_id},
    #         )
    #     new_charge_obj = self.model(
    #         billing_profile = billing_profile,
    #         stripe_id  = c.id,
    #         paid = c.paid,
    #         refunded = c.refunded,
    #         outcome = c.outcome,
    #         outcome_type = c.outcome['type'],
    #         seller_message = c.outcome.get('seller_message'),
    #         risk_level = c.outcome.get('risk_level'),
    #         )
    #     print(c)
    #     new_charge_obj.save()
    #     return new_charge_obj, new_charge_obj.seller_message

class ChargeManager(models.Manager):
    def new(self, order, response): # Charge.objects.do()
        timestamp = response['paid_at']
        local_tz = pytz.timezone("Asia/Seoul") 
        utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        local_dt = local_tz.normalize(utc_dt.astimezone(local_tz))
        new_charge_obj = self.model(
            order=order,
            paid=True,
            customer_uid=response['customer_uid'],
            merchant_uid=response['merchant_uid'],
            amount=response['amount'],
            imp_uid=response['imp_uid'],
            pg_tid=response['pg_tid'],
            receipt_url=response['receipt_url'],
            status=response['status'],
            timestamp=local_dt
            )
        new_charge_obj.save()
        return new_charge_obj


class Charge(models.Model):
    order   = models.ForeignKey('orders.Order', null=True, blank=True, on_delete=models.CASCADE)

    paid            = models.BooleanField(default=False)
    cancelled       = models.BooleanField(default=False)
    refunded        = models.BooleanField(default=False)
    
    customer_uid    = models.CharField(max_length=200, blank=True, null=True)
    merchant_uid    = models.CharField(max_length=200, blank=True, null=True)
    amount          = models.IntegerField(default=0, blank=True, null=True)
    imp_uid         = models.CharField(max_length=200, blank=True, null=True)
    pg_tid          = models.CharField(max_length=200, blank=True, null=True)
    receipt_url     = models.CharField(max_length=200, blank=True, null=True)
    status          = models.CharField(max_length=20, blank=True, null=True)
    timestamp       = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.imp_uid

    objects = ChargeManager()

# import stripe
# stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
# stripe.Charge.create(
#   amount=2000,
#   currency="usd",
#   source="tok_mastercard",
#   description="My First Test Charge (created for API docs)",


# class ChargeIamport(models.Model):
#     billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
#     stripe_id       = models.CharField(max_length=120)
#     paid            = models.BooleanField(default=False)
#     refunded        = models.BooleanField(default=False)
#     outcome         = models.TextField(null=True, blank=True)
#     outcome_type    = models.CharField(max_length=120, null=True, blank=True)
#     seller_message  = models.CharField(max_length=120, null=True, blank=True)
#     risk_level      = models.CharField(max_length=120, null=True, blank=True)