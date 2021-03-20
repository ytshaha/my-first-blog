from django import forms

from .models import Product, Brand, Category, ProductItem, ProductImage
from shop.widgets import XDSoftDateTimePickerInput




class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('number', 'title', 'brand','category', 'list_price',
                  'info_made_country', 'info_product_number', 'info_delivery', 
                  'description', 'main_image', 'video_link',
                  'image1', 'image2', 'image3', 'image4', 'image5', 
                  'image6', 'image7', 'image8', 'image9', )

class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = ProductImage
        fields = ('image', )


# class ProductItemForm(forms.ModelForm):
#     class Meta:
#         model = ProductItem
#         fields = ('product','info_delivery_from','amount','price','product_type',
#                   'price_step','bidding_start_date','bidding_end_date',)

class ProductItemForm(forms.ModelForm):
    product             = forms.ModelChoiceField(queryset=Product.objects.all(), label='물품명')
    bidding_start_date  = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'])#, widget=XDSoftDateTimePickerInput())
    bidding_end_date    = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'])#, widget=XDSoftDateTimePickerInput())

    class Meta:
        model = ProductItem
        fields = ('product','info_delivery_from','amount','price','product_type',
                  'price_step','bidding_start_date','bidding_end_date',)
