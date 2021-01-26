from django import forms

from .models import BuyingTicket

class BuyingTicketForm(forms.ModelForm):

    class Meta:
        model = BuyingTicket
        fields = ('amount',)