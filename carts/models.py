from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed

from products.models import Product


User = settings.AUTH_USER_MODEL

PRODUCT_TYPE = (
    ('normal','상시상품구매'),
    ('bidding','경매상품구매'),
)


class CartItemManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        product_id = request.POST.get('product_id') # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product넣자. 
        product_type = request.POST.get('product_type') # POST가 안먹힐수도 있다. 그렇게 되면 함수의 parameter에 product_type넣자. 
        product_obj = Product.objects.get(id=product_id)
        qs = self.get_queryset().filter(user=user, product=product_obj, product_type=product_type)
        if qs.exists():
            new_obj = False
            cart_item_id = qs.first()
        else:
            cart_item_id = self.new(user=user, product=product_obj, product_type=product_type)
            new_obj = True
        return cart_item_id, new_obj

    def new(self, user, product, product_type):
        return self.model.objects.create(user=user, product=product, product_type=product_type)


class CartItem(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount          = models.IntegerField(default=1)
    price           = models.IntegerField(default=0, help_text=u'단가')
    subtotal        = models.IntegerField(default=0, help_text=u'카트총액')
    product_type    = models.CharField(max_length=20, default='bidding', choices=PRODUCT_TYPE)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = CartItemManager()
    
    def __str__(self):
        return "{}_{}_{}".format(str(self.product.title), str(self.product_type), str(self.user))

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
            if request.user.is_authenticated and cart_obj.user is None: # 비회원으로 들어온 카트를 로긴후에도 사용하기 위해 
                cart_obj.user = request.user
                cart_obj.save()
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
    # products    = models.ManyToManyField(Product, blank=True)
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