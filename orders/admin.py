from django.contrib import admin

from .models import Order, OrderAddress #, TicketOrder
# Register your models here.
admin.site.register(Order)
admin.site.register(OrderAddress)

# admin.site.register(TicketOrder)

# admin.site.register(TicketOrder)

