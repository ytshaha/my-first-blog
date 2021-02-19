from django.contrib import admin

from .models import Ticket, TicketCart

admin.site.register(Ticket)
admin.site.register(TicketCart)

# Register your models here.
