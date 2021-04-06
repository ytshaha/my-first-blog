from django import forms
from django.contrib import messages

from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Card


# class CardRegisterForm(forms.ModelForm):
#     """
#     카드등록하는 폼
#     카드이름만 설정하믄 끝남.
#     customer_uid 는 cus_id_username_# 순으로 자동생성되게 할 예정. 그건 form_valid에서 하믄 됨.
#     -> 이걸 폼에서 하는게 나을지 뷰가 나을지 모델이 나을지는 나도 잘모르겠다. 
#     일단 익숙한 뷰에서 하겠다.
#     """
    
#     class Meta:
#         model = Card
#         fields = ('card_name',)
#         widgets = {
#             'card_name': forms.TextInput(attrs={'class':'form-control'}),
#         }
#         labels = {
#             'username':  ('카드이름(별칭)'),
#         }