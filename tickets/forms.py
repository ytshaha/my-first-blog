from django import forms

from .models import Ticket, TicketItem

class TicketForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ('ticket_id','user','active','bidding_success',)

class TicketItemForm(forms.ModelForm):
    
    class Meta:
        model = TicketItem
        fields = ('tickets_type',)