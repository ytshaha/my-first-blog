from django import forms

from products.models import Product, ProductItem, ProductImage
from shop.widgets import XDSoftDateTimePickerInput

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('number', 'title', 'brand','category', 'list_price',
                  'info_made_country', 'info_product_number', 'info_delivery', 
                  'combined_delivery', 'description', 'video_link',
                  'main_image', 'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 
                  'image7', 'image8', 'image9', )

class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = ProductImage
        fields = ('image', )