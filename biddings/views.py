from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from products.models import Product
from tickets.models import Ticket
from .models import Bidding
from .forms import BiddingForm, BiddingBuyForm

# 새로운 비딩을 시작하고 혹은 있는 비딩이 있으면 가격과 timestam[를 업뎃하는 것.]
# 시간안에 끝났는지를 product의 비딩끝타임으로 확인하여 비딩참여가능한지 홛ㄱ인.
# new_or_get으로하다.
# 기본적으로 유저만 넣었으므로 product와 price등을 입력해야함.
# product에서 비딩참여를 눌렀으므로 form의 post로 product의 슬러그를확인하여 하자. 슬러그로 들어가려고하니까.
# def bidding_new(request):
@login_required
def bidding_new(request, slug):
    # 비딩참여 가능한지 티켓 activate상태 확인.
    user = request.user
    ticket_qs = Ticket.objects.filter(user=user, status='activate')
    if not ticket_qs.exists():
        messages.success(request, "경매에 참여하기 위해서는 티켓이 필요합니다. 티켓을 구매하고 활성화 시키십시오.")
        return redirect("tickets:home")
    # 티켓이 activate일때 아래 항목 발동. 모델에서 티켓검증은 뺀다.
    products = Product.objects.all()
    product_obj = Product.objects.get(slug=slug)
    price_step = range(
                       product_obj.current_price + product_obj.price_step, 
                       product_obj.limit_price + product_obj.price_step, 
                       product_obj.price_step
                       )
    print(product_obj.current_price)
    print(price_step)
    # product_slug = request.session.get('slug')
    if request.method == 'POST':
        form = BiddingForm(request.POST)
        if form.is_valid():
            bidding_obj, updated = Bidding.objects.new_and_update(request, slug=slug)
            product_id = request.POST.get('product', None)
            bidding_price = request.POST.get('bidding_price', None)
            bidding_price = int(bidding_price)
            product_obj = Product.objects.get(id=product_id)
            bidding_obj.bidding_price = bidding_price
            product_obj.current_price = bidding_price
            bidding_obj.product = product_obj
            bidding_obj.timestamp = timezone.now()
            bidding_obj.save()
            product_obj.save()
            return redirect('products:product_detail_slug', slug=slug)
    
    # POST가 아니거나 POST더라도 form이 안채워졌을때..
    form = BiddingForm()
    context = {
        'price_step': price_step,
        'products':products,
        'product_obj':product_obj,
        'form': form,
        'slug': slug
        }
    # return render(request, 'biddings/bidding_new.html', {'form':form, 'product_slug':product_slug})
    return render(request, 'biddings/bidding_new.html', context)


@login_required
def bidding_result(request, slug):
    pass
    '''
    product_detail의 버튼을 비딩유무에 따라 다르게 해야함.
    비딩기간에는 비딩참여 버튼을 비활성화하고 비딩중엔 활성화, 비딩후엔 비딩결과보기 혹은 비활성화 혹은 구매.(당첨자에게만 가능하게.) 
    비딩결과는 어느거랑 비슷할까 생각해보면... cart끝? 이랑 비슷하지 않을까..
    모든 비딩결과는 bidding_end_date 이후에 진행되므로 그것에 대한 확인 필요.
    비딩이후 구매에 대해서는 bidding 우승한 사용자에 대한 검증 확인 필요.
    비딩결과 페이지는 jquery로 띄우든가.. 아니면 product_detial 페이지에 넘기든가. 해여할듯.
    이 모든것이 프로덕트 디테일 페이지 안에 띄워야 하는 것 때문에 비딩뷰가 좀 애매해졌다.
    아니면 결과를 Product모델에다가 넘기는 것은 어떨까? 단 결과에 대한 값을 자동으로 넘겨야하는데 그걸
    어떻게 하는지가 관건...
    scheduling이라는 개념이 들어가고 celery라고 하는 모듈의필요성이 느껴진다.
    일단 결과뽑는건 아래 shell에서 한걸로 하믄 되니까 해보자.
    '''
    product_obj = Product.objects.get(slug=slug)
    bidding_end_date = product_obj.bidding_end_date
    product_amount = product_obj.amount 

    qs = Bidding.objects.filter(product=product_obj, active=True)
    bidding_count = qs.count()
    if bidding_count > product_amount:
        win = product_amount
    else:
        win = bidding_count
    qs_win = qs.order_by("-bidding_price")[:win]
    qs_win_pk = qs_win.values('pk')
    qs.filter(pk__in=qs_win_pk).update(win=True)

    context = {
            'product': product_obj,
            'biddings': qs_win,
            'slug': slug,
            'form':BiddingBuyForm
            }
            # 이거 다 get_query로 돌릴 수 있을거 같은데? 
    return render(request, 'biddings/bidding_result.html', context)
    
# >>> a = qs_now[:2]
# >>> a
# <QuerySet [<Bidding: ytshaha_2o49eic6ro>, <Bidding: test1_6yld9mzd4e>]>
# >>> a.update(win=True
# ... )
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
#   File "D:\django\myvenv\lib\site-packages\django\db\models\query.py", line 688, in update
#     "Cannot update a query once a slice has been taken."
# AssertionError: Cannot update a query once a slice has been taken.
# >>> a.values('pk')
# <QuerySet [{'pk': 32}, {'pk': 33}]>
# >>> q = a.values('pk')
# >>> qs_now
# <QuerySet [<Bidding: ytshaha_2o49eic6ro>, <Bidding: test1_6yld9mzd4e>, <Bidding: ytshaha_qvmlfjrymf>]>
# >>> qs_now.filter(pk__in=q).update(win=True)
# 2
# >>> qs_now
# <QuerySet [<Bidding: ytshaha_2o49eic6ro>, <Bidding: test1_6yld9mzd4e>, <Bidding: ytshaha_qvmlfjrymf>]>
# >>> qs_now[0]
# <Bidding: ytshaha_2o49eic6ro>
# >>> qs_now[0].win
# True
# >>> qs_now[1].win
# True