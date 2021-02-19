from django import forms

from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('title', 'number','brand','start_price','limit_price', 'list_price', 
                  'info_made_country', 'info_product_number', 'info_delivery','info_delivery_from', 
                  'description','amount','bidding_start_date','bidding_end_date','category','image',)

class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = ProductImage
        fields = ('image', )
