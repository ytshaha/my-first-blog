from django import forms

from .models import Product

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('title', 'number','brand','start_price','limit_price','description','amount','bidding_start_date','bidding_end_date','category','image',)

