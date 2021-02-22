import math
from django.db import models
from django.db.models.signals import pre_save, post_save

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
from tickets.models import TicketCart
from mysite.utils import unique_order_id_generator


ORDER_STATUS_CHOICES = (
    ('created','Created'),
    ('paid','Paid'),
    ('shipped','Shipped'),
    ('refunded','Refunded'),
)
   
# class AbstractOrder(models.Model):
#     billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
#     order_id            = models.CharField(max_length=120, blank=True)
#     shipping_address    = models.ForeignKey(Address, related_name='shopping_address', null=True, blank=True, on_delete=models.CASCADE)
#     billing_address     = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True, on_delete=models.CASCADE)
#     status              = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
#     shipping_total      = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
#     total               = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
#     active              = models.BooleanField(default=True)

#     class Meta:
#         abstract = True

class OrderManager(models.Manager):
    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(billing_profile=billing_profile, cart=cart_obj, active=True, status='created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(billing_profile=billing_profile, cart=cart_obj)
            created = True
        return obj, created
    
    # def new_or_get_ticket(self, billing_profile, ticketcart_obj):
    #     created = False
    #     is_cart = False
    #     qs = self.get_queryset().filter(billing_profile=billing_profile, ticketcart=ticketcart_obj, active=True, status='created')
    #     if qs.count() == 1:
    #         obj = qs.first()
    #     else:
    #         obj = self.model.objects.create(billing_profile=billing_profile, ticketcart=ticketcart_obj)
    #         created = True
    #     return obj, created, is_cart

class Order(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
    order_id            = models.CharField(max_length=120, blank=True)
    shipping_address    = models.ForeignKey(Address, related_name='shopping_address', null=True, blank=True, on_delete=models.CASCADE)
    billing_address     = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True, on_delete=models.CASCADE)
    cart                = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True, null=True)
    status              = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total      = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    total               = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active              = models.BooleanField(default=True)

    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([cart_total, shipping_total])
        formatted_total = format(new_total, '2f')
        self.total = formatted_total
        self.save()
        return new_total

    def check_done(self):
        billing_profile = self.billing_profile
        shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if billing_profile and shipping_address and billing_address and total >0:
            return True
        return False

    def mark_paid(self):
        if self.check_done():
            self.status = 'paid'
            self.save()
        return self.status

def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()


post_save.connect(post_save_cart_total, sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    print("running")
    if created:
        # if is_cart:
        print('updating ...first')
        instance.update_total()
        # else:
        #     print('updating ticket cart...first')
        #     instance.update_total_ticket()
post_save.connect(post_save_order, sender=Order)




class TicketOrderManager(models.Manager):
    def new_or_get(self, billing_profile, ticketcart_obj):
        created = False
        qs = self.get_queryset().filter(billing_profile=billing_profile, ticketcart=ticketcart_obj, active=True, status='created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            # 강제로 여기서 total을 매겼다... 
            # 하지만 나중에 갯수를 수정하면 다시 업뎃해야하기 때문에
            # 지금은 ticketcart가 수정되면 무조건 새 order를 만들게 해야함.
            # 나중에 꼭 참고할 것.
            obj = self.model.objects.create(billing_profile=billing_profile, ticketcart=ticketcart_obj, total=ticketcart_obj.total)
            created = True
        return obj, created

class TicketOrder(models.Model):
    # 배송되는것이 아니기 때문에 아래 것들은 딱히 필요는 없다.
    # billing_address 정도는 필요한데... 
    # shipping_total      = models.DecimalField(default=0, max_digits=100, decimal_places=2) # 필요없다.
    
    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
    order_id            = models.CharField(max_length=120, blank=True)
    ticketcart          = models.ForeignKey(TicketCart, on_delete=models.CASCADE)
    shipping_address    = models.ForeignKey(Address, related_name='ticketorder_shopping_address', null=True, blank=True, on_delete=models.CASCADE)
    billing_address     = models.ForeignKey(Address, related_name='ticketorder_billing_address', null=True, blank=True, on_delete=models.CASCADE)
    status              = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total      = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    total               = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active              = models.BooleanField(default=True)



    objects = TicketOrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        ticketcart_total = self.ticketcart.total
        self.total = ticketcart_total
        self.save()
        return ticketcart_total

    def check_done(self):
        billing_profile = self.billing_profile
        billing_address = self.billing_address
        total = self.total
        if billing_profile and billing_address and total >0:
            return True
        return False

    def mark_paid(self):
        if self.check_done():
            self.status = 'paid'
            self.save()
        return self.status

def pre_save_create_ticketorder_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = TicketOrder.objects.filter(ticketcart=instance.ticketcart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(pre_save_create_ticketorder_id, sender=TicketOrder)

def post_save_ticketcart_total(sender, instance, created, *args, **kwargs):
    if not created:
        ticketcart_obj = instance.ticketcart
        ticketcart_total = ticketcart_obj.total
        qs = TicketOrder.objects.filter(ticketcart__id=ticketcart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_ticketcart_total, sender=TicketCart)

def post_save_ticketorder(sender, instance, created, *args, **kwargs):
    print("running")
    if created:
        # if is_cart:
        print('updating ...first')
        instance.update_total()
        # else:
        #     print('updating ticket cart...first')
        #     instance.update_total_ticket()
post_save.connect(post_save_ticketorder, sender=Order)



#################
# 여기는 진짜 없어도 될것 같음.
# def post_save_ticketlist_total(sender, instance, created, *args, **kwargs):
#     if not created:
#         ticketlist_obj = instance
#         ticketlist_total = ticketlist_obj.total
#         ticketlist_id = ticketlist_obj.id
#         qs = TicketOrder.objects.filter(ticketlist__id=ticketlist_id)
#         if qs.count() == 1:
#             ticketorder_obj = qs.first()
#             ticketorder_obj.update_total()

# post_save.connect(post_save_ticketlist_total, sender=TicketList)

# def post_save_ticketorder(sender, instance, created, *args, **kwargs):
#     print("running")
#     if created:
#         print('updating...first')
#         instance.update_total()

# post_save.connect(post_save_ticketorder, sender=TicketOrder)
