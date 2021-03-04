from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed

from products.models import Product, ProductItem
from tickets.models import TicketItem


User = settings.AUTH_USER_MODEL

PRODUCT_TYPE = (
    ('normal','상시상품구매'),
    ('bidding','경매상품구매'),
    ('ticket','경매티켓구매'),
    
)


class CartItemManager(models.Manager):#################210303_여기 좀 나중에 수정 필요.....
    def new_or_get(self, request, temp_id=None):
        user = request.user
        product_type = request.POST.get('product_type')
        
        try:
            at_cart = request.POST.get('at_cart')
        except:
            at_cart = False

        # 카트에서 remove로 호출된 경우
        if at_cart:
            cart_item_id = request.POST.get('cart_item_id')
            cart_item_qs = self.get_queryset().filter(id=cart_item_id)
            cart_item_obj = cart_item_qs.first()
            new_obj = False
            return cart_item_obj, new_obj

        # 티켓구매나 물품구매에서 호출된 경우
        if product_type == 'bidding' or product_type == 'normal':
            # product_item_id = request.POST.get('product_item_id') # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
            product_item_obj = ProductItem.objects.get(id=temp_id)
            # ticket_item_id = None
            ticket_item_obj = None
        elif product_type == 'ticket':
            # ticket_item_id = request.POST.get('ticket_item_id') # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
            ticket_item_obj = TicketItem.objects.get(id=temp_id)
            # product_item_id = None
            product_item_obj = None
        else:
            raise Http404

        qs = self.get_queryset().filter(user=user, product_item=product_item_obj, ticket_item=ticket_item_obj, product_type=product_type)
        if qs.exists():
            new_obj = False
            cart_item_obj = qs.first()
        else:
            cart_item_obj = self.new(user=user, product_item=product_item_obj, ticket_item=ticket_item_obj, product_type=product_type)
            new_obj = True
        return cart_item_obj, new_obj

    def new(self, user, product_item, ticket_item, product_type):
        return self.model.objects.create(user=user, product_item=product_item, ticket_item=ticket_item, product_type=product_type)


class CartItem(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item    = models.ForeignKey(ProductItem, blank=True, null=True, on_delete=models.CASCADE)
    ticket_item     = models.ForeignKey(TicketItem, blank=True, null=True, on_delete=models.CASCADE)
    amount          = models.IntegerField(default=1)
    price           = models.IntegerField(default=0, help_text=u'단가')
    subtotal        = models.IntegerField(default=0, help_text=u'카트총액')
    product_type    = models.CharField(max_length=20, default='bidding', choices=PRODUCT_TYPE)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = CartItemManager()
    
    def __str__(self):
        if self.product_type == 'ticket':
            return "{}_{}_{}".format(str(self.product_type), str(self.ticket_item.tickets_type), str(self.user))
        elif self.product_type == 'bidding' or self.product_type == 'normal':
            return "{}_{}_{}".format(str(self.product_type), str(self.product_item.product.title), str(self.user))
        else:
            return self.id

def pre_save_cart_item_receiver(sender, instance, *args, **kwargs):
    instance.subtotal = int(instance.price) * int(instance.amount)

pre_save.connect(pre_save_cart_item_receiver, sender=CartItem)




class CartManager(models.Manager):

    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
        else:
            cart_obj = self.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    user        = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    cart_items  = models.ManyToManyField(CartItem, blank=True)
    subtotal    = models.IntegerField(default=0)
    total       = models.IntegerField(default=0)
    updated     = models.DateTimeField(auto_now_add=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    objects = CartManager()


    def __str__(self):
        return str(self.id)




def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        cart_items = instance.cart_items.all()
        total = 0
        for x in cart_items: # x는 개별 cart_items
            total += x.subtotal

        if instance.subtotal != total:
            instance.subtotal = total
            instance.save()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.cart_items.through)

def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = instance.subtotal # 8% tax
    else:
        instance.total = 0.00
pre_save.connect(pre_save_cart_receiver, sender=Cart)