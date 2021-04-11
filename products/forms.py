from django import forms

from .models import Product, Brand, Category, ProductItem, ProductImage
from shop.widgets import XDSoftDateTimePickerInput




class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('number', 'title', 'brand','category', 'list_price',
                  'info_made_country', 'info_product_number', 'info_delivery', 'combined_delivery',
                  'description', 'main_image', 'video_link',
                  'image1', 'image2', 'image3', 'image4', 'image5', 
                  'image6', 'image7', 'image8', 'image9', )
        # widgets = {

        #     'username': forms.TextInput(attrs={'class':'form-control'}),
        #     'email': forms.EmailInput(attrs={'class':'form-control'}),
        #     'full_name': forms.TextInput(attrs={'class':'form-control'}),
        #     'phone_number': forms.TextInput(attrs={'class':'form-control'}),
            # 'password1': forms.PasswordInput(attrs={'class':'form-control'}),
            # 'password2': forms.PasswordInput(attrs={'class':'form-control'}),
        # }
        labels = {
            'number': ('상품번호'),
            'title': ('상품명'),
            'brand': ('브랜드'),
            'category': ('카테고리'),
            'list_price': ('리테일가격'),
            'info_made_country': ('제조국'),
            'info_product_number': ('제품번호'),
            'info_delivery': ('배송방법'),
            'description': ('상세설명'),
            'main_image': ('메인이미지'),
            'video_link': ('유튜브링크'),
        }


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
        fields = (
                   'product',
                   'product_type',
                   'info_delivery_from',
                   'option',
                   'amount',
                   'start_price',
                   'price',
                   'price_step',
                   'bidding_start_date',
                   'bidding_end_date',
                   'featured',
                )

        labels = {
            'product': ('물품'),
            'product_type': ('물품타입'),
            'info_delivery_from': ('배송지'),
            'option': ('옵션유무'),
            'amount': ('수량'),
            'start_price': ('경매시작가격'),
            'price': ('경매종료가격'),
            'price_step': ('경매가격스텝'),
            'bidding_start_date': ('경매시작일시'),
            'bidding_end_date': ('경매종료일시'),
            'featured': ('활성화여부'),
        }


