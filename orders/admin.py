from django.contrib import admin

from .models import Order, TicketOrder
# Register your models here.
admin.site.register(Order)
admin.site.register(TicketOrder)

# admin.site.register(TicketOrder)

