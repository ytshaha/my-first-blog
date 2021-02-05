from django import forms

from .models import Product

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('title', 'number','brand','start_price','limit_price','info','amount','bidding_date','category','image',)

