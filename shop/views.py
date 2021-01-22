from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

# Create your views here.
def first_page(request):
    return render(request, 'shop/first_page.html', {})

def index(request):
    return render(request, 'shop/index.html', {})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products':products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product':product})

def buying_ticket(request):
    # 여기는 티켓을 사기만 하면 되니까 폼으로 넘기는게 좋을듯. 
    # 드랍다운 메뉴로 티켓종류 고르고 유저는 현재 로긴한 유저로 하고 
    # 단 티켓을 산 시점을 기점으로 횟수인지 날짜인지에 따라 유효기간을 만들수 있어야함. 
    # 당장은 기간으로만 하는게 어떠함;아니다 사람들은 물품을 보고 들어오지 맨날 사려고는 안할거다.
    # 그러면 티켓을 사용한 날을 기존에 누적해서 갯수가 되면 떼네야하나.... 생각보다 티켓이 어렵네.
    return render(request, 'shop/buying_ticket.html', {})