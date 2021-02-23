from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save, post_save
from django.conf import settings

from products.models import Product
from tickets.models import Ticket
from mysite.utils import unique_slug_generator, unique_bidding_id_generator
# from tickets.models import Ticket

User = settings.AUTH_USER_MODEL

# Create your models here.

class BiddingManager(models.Manager):
    '''
    프로덕트의 슬러그를 넘겨서 페이지를 만드는게
    그렇게 좋지는 않은것 같다. 
    기왕이면 product_id나 pk나 number
    일단 되게하는 것이 중요하니까 넘어가자.
    '''
    def new_and_update(self, request, slug=None):
        
        user = request.user
        slug = slug
        # 일단 티켓이 엑티베이트인지 확인
        ticket_qs = Ticket.objects.filter(user=user, status='activate')
        
        # bidding_id = request.session.get("bidding_id", None)
        product_obj = Product.objects.get(slug=slug)

        qs = self.get_queryset().filter(user=user, product=product_obj)
        print('qs길이가 1나이면 좋긴한데 아니면 .first를 해줘야함..')
        print(qs)
        if request.user.is_authenticated: # 로긴한것과 activate 티켓있는지 확인.나중에는 일정등급 user인지만 확인하게하자. 
            if qs.exists():
                updated = True
                qs.update(active=False)
                bidding_obj = self.new(user=user)
                return bidding_obj, updated
            else:
                bidding_obj = self.new(user=user)
                updated = False
                # request.session['bidding_id'] = bidding_obj.id
            return bidding_obj, updated

    def new(self, user=None):
        user_obj = user
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Bidding(models.Model):
    bidding_id      = models.CharField(max_length=100, blank=True, null=True) # 얘또한 아이디+slug조합으로 만들자.
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    bidding_price   = models.PositiveIntegerField(default=0, help_text=u'경매참여가격') # 얘보다 높아야 참여가능하겠지.
    timestamp       = models.DateTimeField(auto_now_add=True)
    win             = models.BooleanField(default=False)
    active          = models.BooleanField(default=True) # 비딩을 새로 올릴때 나머지 낮은 가격대의 비딩들을 다 False로 만든다.
    
    objects = BiddingManager()

    def __str__(self):
        return self.bidding_id


def bidding_pre_save_receiver(sender, instance, *args, **kwargs):
    # 슬러그 설정
    if not instance.bidding_id:
        username = instance.user.get_username()
        instance.bidding_id = unique_bidding_id_generator(instance, username)
    
pre_save.connect(bidding_pre_save_receiver, sender=Bidding)