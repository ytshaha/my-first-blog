from django.shortcuts import render, get_object_or_404, redirect
from .models import BuyingTicket
from django.contrib.auth.decorators import login_required
from .forms import BuyingTicketForm

from django.views import generic
# from .forms import PostForm, CommentForm
from django.core.files.storage import FileSystemStorage
from products.models import Product, ProductItem

def index(request):
    product_items_normal = ProductItem.objects.get_normal().filter(featured=True)[:6]
    product_items_bidding = ProductItem.objects.get_bidding().filter(featured=True)[:6]
    
    print("Current request.session.")
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))

    context = {
        'product_items_normal': product_items_normal,
        'product_items_bidding': product_items_bidding
    }
    return render(request, 'shop/index.html', context)

def introduction(request):
    return render(request, 'shop/introduction.html', {})

def temp(request):
    return render(request, 'shop/google6d21af56577f529f.html', {})

def faq(request):
    return render(request, 'shop/faq.html', {})



@login_required
def buying_ticket(request):
    # 여기는 티켓을 사기만 하면 되니까 폼으로 넘기는게 좋을듯. 
    # 드랍다운 메뉴로 티켓종류 고르고 유저는 현재 로긴한 유저로 하고 
    # 단 티켓을 산 시점을 기점으로 횟수인지 날짜인지에 따라 유효기간을 만들수 있어야함. 
    # 당장은 기간으로만 하는게 어떠함;아니다 사람들은 물품을 보고 들어오지 맨날 사려고는 안할거다.
    # 그러면 티켓을 사용한 날을 기존에 누적해서 갯수가 되면 떼네야하나.... 생각보다 티켓이 어렵네.

    # 2021/1/27 지금은 그냥 save하면 바로 티켓이 나온다. 
    # 하지만 실제로는 구매를 해야지 티켓이 나와야한다. 
    # 그래서 model에 구매여부를 받아서 유효여부라는 걸 만들어야할거같다. 
    # 구매여부&미사용 조건으로 유효, 둘중하나라도 만족못하면 사용불가.
    # 그럴래면 결국 구매라는 것으로 넘어가야하는데 일단 넘어가자.
    # 그리고 제네릭뷰를 빨리 배워야할듯하다. 제네릭뷰의 template어떻게하는지도..
    if request.method == 'POST':
        buying_tickets = BuyingTicket.objects.all()
        form = BuyingTicketForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.buying_number = buying_tickets.count() + 1
            post.save()
            return redirect('buying_ticket_result', pk=post.pk)
    else:
        form = BuyingTicketForm()
    return render(request, 'shop/buying_ticket.html', {'form':form})

class BuyingTicketResultView(generic.DetailView):
    model = BuyingTicket
    template_name = 'shop/buying_ticket_result.html'
    context_object_name = 'buying_ticket'


@login_required
def bidding(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/bidding.html', {'product':product})

# @login_required
# def buying_ticket_result(request, pk):
#     buying_ticket = get_object_or_404(BuyingTicket, pk=pk)
#     return render(request, 'shop/buying_ticket_result.html', {'buying_ticket':buying_ticket})

