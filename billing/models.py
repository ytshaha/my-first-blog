from django.conf import settings
from django.db import models

from django.db.models.signals import post_save

User = settings.AUTH_USER_MODEL
# Create your models here.

class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

# customer_id in Stripe or Braintree가 생기면 부활할겅다. 
# def billing_profile_created_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         print("ACTURE API REQUEST Send to stripe")
#         instance.customer_id = newID
#         instance.save()

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)