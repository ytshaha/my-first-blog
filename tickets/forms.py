from django import forms

from .models import Ticket, TicketCart

class TicketForm(forms.ModelForm):
    
    class Meta:
        model = Ticket
        fields = ('ticket_id','user','active','bidding_success',)

class TicketCartForm(forms.ModelForm):
    
    class Meta:
        model = TicketCart
        fields = ('tickets_type',)