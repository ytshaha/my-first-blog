from django.db import models

from billing.models import BillingProfile

ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping')
)

class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    email           = models.EmailField(max_length=255)
    phone_number    = models.CharField(max_length=255, blank=True, null=True)
    full_name       = models.CharField(max_length=255, blank=True, null=True)
    
    address_type    = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    address_line_1  = models.CharField(max_length=120)
    address_line_2  = models.CharField(max_length=120, null=True, blank=True)
    postal_code     = models.CharField(max_length=120)
    timestamp       = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.billing_profile)
    
    def get_address(self):
        return "{line1} {line2}({postal})".format(
            line1 = self.address_line_1,
            line2 = self.address_line_2,
            postal = self.postal_code
        )

    def get_postal_code(self):
        return self.postal_code

