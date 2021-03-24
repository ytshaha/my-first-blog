from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.utils import timezone

from products.models import Product, ProductItem
from biddings.models import Bidding
from tickets.models import TicketItem


User = settings.AUTH_USER_MODEL

PRODUCT_TYPE = (
    ('normal','상시상품구매'),
    ('bidding','경매상품구매'),
    ('ticket','경매티켓구매'),
    
)

CART_ITEM_STATUS_CHOICES = (
    ('created','Created'),
    ('paid','Paid'),
)

class CartItemManager(models.Manager):#################210303_여기 좀 나중에 수정 필요.....
    def new_or_get(self, request, temp_id=None):
        user = request.user
        product_type = request.POST.get('product_type', None)
        option = request.POST.get('option', None)
        at_cart = request.POST.get('at_cart', None)

        # 카트에서 remove로 호출된 경우
        if at_cart:
            cart_item_id = request.POST.get('cart_item_id', None)
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

        qs = self.get_queryset().filter(user=user, product_item=product_item_obj, ticket_item=ticket_item_obj, product_type=product_type).exclude(status='paid')
        if qs.exists():
            new_obj = False
            cart_item_obj = qs.first()
            cart_item_obj.option = option
            cart_item_obj.save()
        else:
            cart_item_obj = self.new(user=user, product_item=product_item_obj, ticket_item=ticket_item_obj, product_type=product_type, option=option)
            new_obj = True
        return cart_item_obj, new_obj

    def new(self, user, product_item, ticket_item, product_type, option):
        return self.model.objects.create(user=user, product_item=product_item, ticket_item=ticket_item, product_type=product_type, option=option)


class CartItem(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item    = models.ForeignKey(ProductItem, blank=True, null=True, on_delete=models.CASCADE)
    ticket_item     = models.ForeignKey(TicketItem, blank=True, null=True, on_delete=models.CASCADE)
    option          = models.CharField(max_length=20, default=0, blank=True, null=True, help_text=u'옵션')
    amount          = models.IntegerField(default=1)
    price           = models.IntegerField(default=0, help_text=u'단가')
    subtotal        = models.IntegerField(default=0, help_text=u'물품 총액')
    total           = models.IntegerField(default=0, help_text=u'기타비용 포함 총액')
    product_type    = models.CharField(max_length=20, default='bidding', choices=PRODUCT_TYPE)
    status          = models.CharField(max_length=120, default='created', choices=CART_ITEM_STATUS_CHOICES)
    timestamp       = models.DateTimeField(auto_now_add=True)
    sale_ratio      = models.DecimalField(default=0, max_digits=100, decimal_places=1, help_text=u'할인율_자동계산필드')
    add_certificate = models.BooleanField(default=False)
    is_reviewed     = models.BooleanField(default=False)

    objects = CartItemManager()
    
    def __str__(self):
        timestamp = self.timestamp
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        formmated_timestamp = "{:04d}{:02d}{:02d}".format(year, month, day)
        if self.product_type == 'ticket':
            return "added_{}_{}_{}".format(formmated_timestamp, str(self.user), str(self.ticket_item) )
        elif self.product_type == 'bidding' or self.product_type == 'normal':
            return "added_{}_{}_{}".format(formmated_timestamp, str(self.user), str(self.product_item))
        else:
            return self.id

def pre_save_cart_item_receiver(sender, instance, *args, **kwargs):
    instance.subtotal = int(instance.price) * int(instance.amount)
    
    # 할인율 계산
    if instance.product_type == 'normal':
        instance.sale_ratio = instance.product_item.sale_ratio
    elif instance.product_type == 'bidding':
        bidding_qs = Bidding.objects.filter(user=instance.user, product_item=instance.product_item, win=True)
        if bidding_qs.count() == 1:
            bidding_obj = bidding_qs.first()
        instance.sale_ratio = bidding_obj.sale_ratio
    if instance.product_type == 'ticket':
        instance.sale_ratio = instance.ticket_item.sale_ratio
    # 정품보증서 가격 추가시 20000원
    if instance.add_certificate:
        instance.total = instance.subtotal + 20000
    else:
        instance.total = instance.subtotal
    
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

    def update_total(self):
        '''
        두가지를 수행함.
        1. cart.total 을 order의 total로 넘겨줌(post_save @ order or cart)
        2. checkout_total을 point를 제외한 금액으로 update
        '''
        cart_items = self.cart_items.all()
        total = 0
        for x in cart_items: # x는 개별 cart_items
            total += x.total
            print("total", total)
        print("업데이트토탈에서 계산된 토탈..", total)
        self.subtotal = total
        self.total = total
        self.save()
        print('z카트의 업데이트토탈 실행.과 새이브')
        print("저장된 카트의 토탈",self.subtotal, self.total)
        print('self의 정채성', self)
        return self.total


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        cart_items = instance.cart_items.all()
        total = 0
        for x in cart_items: # x는 개별 cart_items
            total += x.total
        # instance.update_total()

        if instance.subtotal != total:
            instance.subtotal = total
            instance.total = total
            
            instance.save()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.cart_items.through)

def pre_save_cart_receiver(sender, instance, *args, **kwargs):   
    if instance.subtotal > 0:
        instance.total = instance.subtotal # 8% tax
    else:
        instance.total = 0.00

    # qs = Cart.objects.filter(id=instance.id)
    # if qs.exists():
    #     qs.update(active=False)

# pre_save.connect(pre_save_cart_receiver, sender=Cart)

# def post_save_cart_item_total(sender, instance, created, *args, **kwargs):
#     if not created:
#         print('카트에있는 총액 재계산')
#         cart_obj = Cart.objects.filter(user=instance.user).order_by('-timestamp').first()
#         print("CartItem 세이브하면 post_save되는 cart_obj",cart_obj)
#         # cart_obj = qs.first()
#         cart_obj.update_total()


# post_save.connect(post_save_cart_item_total, sender=CartItem)