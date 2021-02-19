from django import forms

from shop.models import BuyingTicket

class BuyingTicketForm(forms.ModelForm):

    class Meta:
        model = BuyingTicket
        fields = ('amount',)
