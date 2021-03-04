from django import forms

from .models import Product, ProductItem, ProductImage

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('number', 'title', 'brand','category', 'list_price',
                  'info_made_country', 'info_product_number', 'info_delivery', 
                  'description', 'image', 'video_link',)

class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = ProductImage
        fields = ('image', )


class ProductItemForm(forms.ModelForm):
    
    class Meta:
        model = ProductItem
        fields = ('product','info_delivery_from','amount','price','product_type',
                  'price_step','bidding_start_date','bidding_end_date',)


    