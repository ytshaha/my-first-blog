from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from decimal import Decimal
import datetime

# from biddings.models import Bidding
from mysite.utils import unique_ticket_id_generator
TICKETS_TYPES = (
    (1, 1),
    (3, 3),
    (5, 5),
    (10, 10),
    (20, 20),
    (30, 30),
    )

TICKET_STATUS = (
    ('unused', "UNUSED"),
    ('activate', "ACTIVATE"),
    ('used', 'USED'),
    )
User = settings.AUTH_USER_MODEL
# Create your models here.

class TicketManager(models.Manager):
    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

    def get(self, request):
        '''
        Ticket 모델에서 해당 유저가 갖고 있는 모든 ticket들을 보여줌. 
        사용한 티켓 보기 옵션은 일단 넣지 말자.(즉 사용가능한것만).
        user와 active 여부로 filter해서 get_queryset하믄 될듯.
        일단 active상관없이 filter하자. 
        너무 ticket list가 허해보일것같다.. ㅋㅋ
        '''
        user = request.user
        ticket_obj = None
        if user.is_authenticated:
            ticket_obj = self.model.objects.filter(user=user)
        
        return ticket_obj        


class Ticket(models.Model):
    '''
    Ticket 모델
    사용자가 구매한 티켓에 대한 model
    구매하면 구매한만큼 바로 SLUG를 통해 티켓아이디를 만들어주고 
    사용했는지 ACTIVE를 열어놓은 티켓리스트를 주자. 
    구매한 사용자는 티켓을 쿠폰처럼 조회할 수 있어야한다. 
    그래서 그 티켓을 사용하는것은 체크하고 사용... 이런 칸을 TICKET 메뉴에서 선택할 수있게해야한다.
    티켓을 사용할 프로덕트 넘버 혹은 타이틀(?) 등을 연결시켜야한다. 
    타이틀로 하면 나중에 겹칠 수 있으므로 product.number에 연결하는게 나을수도있다.
    * 임시로 비딩을 만들고 class도 만들었다. bidding_id, product, user로 필드구성해놨다.
    티케 구매를 위해서는 결국 ticket order를 만들어서 ticket에 연결이 필요핟.
    그리고 ticket_order에는 billingProfile이 연결되어서 기존의구매시스템에 연결시켜야겠다. 
    '''
    ticket_id       = models.CharField(max_length=40, blank=True)# 아이디 + 10개랜덤슬러그(중복없이)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    # biddings        = models.ForeignKey(Bidding, on_delete=models.CASCADE, blank=True, null=True)# 참여한 Bidding들이다. 
    update          = models.DateTimeField(auto_now=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    
    # 사용여부.., 이것은 티켓홈에서 사용하게 한다
    # 사용하면 사용한 날을 표기한다(update나 timestamp로 해야겠지.)
    # 그리고 pre_save로 사용한 날이 지나면 active를 꺼야한다.(이건 jquery로 해야하나...)
    status           = models.CharField(max_length=20, default='unused', choices=TICKET_STATUS)
    active           = models.BooleanField(default=True)
    bidding_success  = models.BooleanField(default=False) # 비딩성공시 해당 비딩가격은 포인트로 반환해주지 않는다.
    transfer_point   = models.BooleanField(default=False)
    
    objects = TicketManager()

    def __str__(self):
        return self.ticket_id

def pre_save_create_ticket_id(sender, instance, *args, **kwargs):
    if not instance.ticket_id:
        instance.ticket_id = unique_ticket_id_generator(instance)
    
    # 사용되지 않은것 제외하고 오늘보다 timestamp가 작은 user의 ticket은 active False만들어라.
    today = datetime.datetime.now().date()
    qs = Ticket.objects.filter(user=instance.user, timestamp__lt=today).exclude(status='unused')
    if qs.exists():
        qs.update(active=False)
        qs.update(status='used')
        

pre_save.connect(pre_save_create_ticket_id, sender=Ticket)

# 실질적으로 ticket의 cart는 ticketcart가 해줌.
#  같은 오더를 써도 되고 ticker order를 써도될거같음. 
#  그냥 오더는 cart 필드가 있어서 티켓이랑 공유가 불가할 것 같음. 따로 만들자. 
# 그리고 실질적으로 비슷한 프로세스로 진행할것 같으므로 오더앱에 같이 쓰자.
# 
# 물건구매 프로세스 
# product-cart-order- 최종 체크아웃
#               |
#             billingprofile
#               |
#             address
# 
# 티켓구매프로세스
# ticket_buy(cart) - ticket_order- 최종 체크아웃
#                         |
#                   billingprofile
#                         |
#                      address



# 현재는 위와 같이 진행된다. 
# order에 biiling이랑 addre는 별도이다.
#  ticketorder만 따로 만들고 Biiling이랑 Address check아웃은 재활용하자.. 

class TicketItemManager(models.Manager):
    def new_or_get(self, request):
        ticket_item_id = request.session.get("ticket_item_id", None)
        qs = self.get_queryset().filter(id=ticketcart_id)
        if qs.count() == 1:
            new_obj = False
            ticketcart_obj = qs.first()
            if request.user.is_authenticated and ticketcart_obj.user is None: # 비회원으로 들어온 카트를 로긴후에도 사용하기 위해 
                ticketcart_obj.user = request.user
                ticketcart_obj.save()
        else:
            ticketcart_obj = self.new(user=request.user)
            new_obj = True
            request.session['ticketcart_id'] = ticketcart_obj.id
        return ticketcart_obj, new_obj

    def new(self, user, tickets_type):
        user_obj = None
        tickets_type = int(tickets_type)
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj, tickets_type=tickets_type)


class TicketItem(models.Model):
    user            = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    subtotal        = models.IntegerField(default=0)  # 일단 그냥 단순 갯수*5000원 한 값
    total           = models.IntegerField(default=0)  # 할인율을 적용한 값.
    sale_ratio      = models.DecimalField(default=0, max_digits=100, decimal_places=1, help_text=u'할인율')
    timestamp       = models.DateTimeField(auto_now_add=True)
    tickets_type    = models.IntegerField(default=0, choices=TICKETS_TYPES)

    objects = TicketItemManager()

    def __str__(self):
        return str(self.id)


def pre_save_ticket_item_receiver(sender, instance, *args, **kwargs):
    if instance.tickets_type == 1:
        instance.subtotal = 5000
        instance.total = 5000
    elif instance.tickets_type >= 3 and instance.tickets_type < 10:
        instance.subtotal = instance.tickets_type * 5000
        instance.total = instance.tickets_type * 5000 * 0.95 # 5% 할인
    elif instance.tickets_type >= 10:
        instance.subtotal = instance.tickets_type * 5000
        instance.total = instance.tickets_type * 5000 * 0.9 # 10% 할인
    else:
        instance.subtotal = 0.00
        instance.total = 0.00

    if instance.subtotal == 0.00:
        instance.sale_ratio = 0.00
    else:    
        instance.sale_ratio = Decimal(instance.subtotal - instance.total) / instance.subtotal * 100

pre_save.connect(pre_save_ticket_item_receiver, sender=TicketItem)

