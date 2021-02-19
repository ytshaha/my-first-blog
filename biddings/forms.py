from django import forms

from .models import Bidding

class BiddingForm(forms.ModelForm):
    
    class Meta:
        model = Bidding
        fields = ('product','bidding_price',)


            
class BiddingBuyForm(forms.Form):
    product_id = forms.CharField(label='product_id', max_length=256, widget=forms.HiddenInput())

