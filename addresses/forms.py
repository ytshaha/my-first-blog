from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            # 'billing_profile',
            # 'address_type',
            'address_line_1',
            'address_line_2',
            'postal_code',
            ]



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


