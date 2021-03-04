from django.contrib import admin

from .models import Ticket , TicketItem

admin.site.register(Ticket)
admin.site.register(TicketItem)

# Register your models here.
