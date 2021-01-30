from django import forms

from shop.models import BuyingTicket, Product

class BuyingTicketForm(forms.ModelForm):

    class Meta:
        model = BuyingTicket
        fields = ('amount',)

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('product', 'number','brand','start_price','limit_price','info','amount','bidding_date','category','image',)

