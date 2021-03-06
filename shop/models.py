from django.conf import settings
from django.db import models
from django.utils import timezone

class BuyingTicket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text=u'티켓구매자')
    amount = models.IntegerField(default=0, help_text=u'수량')
    buying_number = models.CharField(max_length=200, help_text=u'상품명')
    
    def __str__(self):
        return str(self.user) + "_" + self.buying_number

# class TicketList(models.Model):
#     # 티켓을 횟수로만 발행해야함.(내가 살기 위해서)
#     # 횟수 티켓에 따른 가격이 정해져있을건데 그것을 모델에서 어떻게 정의하지.. 그냥 뷰에서 받아들일때 가격을 해야하나>?
#     # 아니다 구매자도 구매에 따른 가격을 알아야하니까 그냥 등록해놓으면 되겠네.
#     # 구매한 티켓에 대해서만 number를 매기면 될거 같다.
#     name = models.CharField(max_length=200, help_text=u'티켓종류이름') 
#     bidding_amount = models.IntegerField()
#     price = models.IntegerField()

# class Ticket(models.Model):
#     '''
#     Ticket 모델
#     사용자가 구매한 티켓에 대한 model
#     Ticket 사용한 갯수를 기록하기 위해 number, remain_amount를 만들었다.
#     단 remain_amount를 어떻게해야하는지가 궁금한데...
#     횟수권에 따라 따로 모델을 만들어야할지 아니면 ticket 사용 database를 만들어서 해당 ticket사용횟수를 매번기록할지는 미지수
#     매번 기록하는 방식은 내가 임의로 수정이 불가하므로 여기에서 알아서 마무리되게해야할듯.
#     '''
#     number = models.CharField(max_length=8)# 8개자리의 티켓을 만들고 00000001 부터 순차적으로 숫자를 올리는 방식으로 티켓발행 필요.
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     remain_amount = models.IntegerField() # 사용하고 남은 횟수

# class Bidding(models.Model):
#     '''
#     Bidding 모델
#     각 물품에 대해 비딩한 사람, 비딩시 사용한 티켓 및 최종 비딩결과를 도출하기 위한 모델
#     해당 모델을 통해 Ticket횟수를 감소시킬때도 사용한다. 
#     '''
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text=u'유저')
#     product = models.ForeignKey('Product', on_delete=models.CASCADE, help_text=u'물품')
#     bidding_price = models.IntegerField(default=0, help_text=u'비딩가격')
