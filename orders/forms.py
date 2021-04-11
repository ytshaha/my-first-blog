from django import forms

from .models import Order

ORDER_STATUS_CHOICES = (
    ('created','주문생성'),
    ('paid','결제완료'),
    ('shipping','배송중'),
    ('shipped','배송완료'),
    ('refunded','환불완료'),
    ('cancel', '결제취소'),
)


class OrderForm(forms.ModelForm):
    status = forms.ChoiceField(choices=ORDER_STATUS_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Order
        fields = ('status', 'tracking_number',)
        
        labels = {
            'status': ('주문상태'),
            'tracking_number': ('운송장번호'),
        }
        widgets = {
            'status': forms.TextInput(attrs={'class':'form-control'}),
            'tracking_number': forms.TextInput(attrs={'class':'form-control'}),
        }
