from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from billing.models import BillingProfile
from .forms import AddressForm
from .models import Address

@login_required
def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    is_ticket = request.session.get('is_ticket')
    context = {
        "form": form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        instance = form.save(commit=False)

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            request.session[address_type + "_address_id"] = instance.id
            print(address_type + "_address_id")
        else:
            print('Error here')
            if is_ticket:
                return redirect("tickets:checkout-iamport")
            else:
                return redirect("carts:checkout-iamport")
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            if is_ticket:
                return redirect("tickets:checkout-iamport")
            else:
                return redirect("carts:checkout-iamport")
    return redirect("carts:checkout-iamport")

@login_required
def checkout_address_reuse_view(request):
    is_ticket = request.session.get('is_ticket')
    if request.user.is_authenticated:
        context = {}
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == "POST":
            shipping_address = request.POST.get('shipping_address', None)
            address_type = request.POST.get('address_type', 'shipping')
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if shipping_address is not None:
                qs = Address.objects.filter(billing_profile=billing_profile, id=shipping_address)
                if qs.exists():
                    request.session[address_type + "_address_id"] = shipping_address
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
    if is_ticket:
        return redirect("tickets:checkout-iamport")
    else:
        return redirect("carts:checkout-iamport")


    



@login_required
def change_address(request):
    user = request.user

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    shipping_address_obj = None
    billing_address_obj = None

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        # if shipping_address_id:
        if address_qs.filter(address_type='shipping').count() > 0:
            shipping_address_obj = address_qs.filter(address_type='shipping').order_by('-timestamp').first()
            print("shipping_address가 존재합니다.")
        else:
            shipping_address_obj = None
            print("shipping_address가 없습니다.")
        if address_qs.filter(address_type='billing').count() > 0:
            billing_address_obj = address_qs.filter(address_type='billing').order_by('-timestamp').first()
        else:
            billing_address_obj = None
    # 3.  첫 화면 로드 - 주소2개 있을때
    # 주소는 완성되어있게 하고 빌링 주소, 쉬핑주소 같이 나오게(위아래로,)
    # 아직 포스트를 누르지는 않았음.
        context = {
        'billing_profile': billing_profile,
        'shipping_address_obj': shipping_address_obj,
        'billing_address_obj': billing_address_obj,
        'address_qs': address_qs,
        }
    if request.method != 'POST':
        return render(request, "addresses/change_address.html", context)
    

    post_purpose = request.POST.get('post_purpose', None)
    print('post_purpose', post_purpose)
    # 항상 이것으로 끝나게 하면 안되므로 POST가 아니면 아래와 같이 진행되게 하자. 
    # 주소가 있는경우와 없는경우로 나눠지는데 둘다 이후에는 POST를 누를거기 때문에 이렇게 하면 첫화면 구성은 끝날거같다.
    

    # 아임포트 토큰 가져오기
    

    
    if request.method == 'POST' and not post_purpose and not request.is_ajax():
        return render(request, "addresses/change_address.html", context)
    # 4. POST 이후의 화면 구성
    #   1) 주소 수정 눌렀을 때
    #   2) 포인트사용 눌렀을 떄
    #   3) 최종 결재를 눌렀을 때
    # 단 어떤 경우든 바로 결재가 진행될 수 있어야함. 주소가 없는경우를 따로 가정하지는 말자. 그떄는 버튼을 없에버리면 될듯.
    
    # 1) 주소 수정 눌렀을 때
    if request.method == 'POST' and post_purpose == 'change_or_add_address':
        full_name   = request.POST.get('full_name', None)
        email       = request.POST.get('email', None)
        if email == "":
            email = user.email
        phone_number = request.POST.get('phone_number', None)
        address_line_1 = request.POST.get('address_line_1', None)
        address_line_2 = request.POST.get('address_line_2', None)
        postal_code = request.POST.get('postal_code', None)
        order_memo = request.POST.get('order_memo', None)
        # address_type = request.POST.get('address_type', None)
        
        # 폼이 제대로 완성되어있지 않았을 경우
        print(full_name, email, phone_number, address_line_1, address_line_2, postal_code)
        if not full_name or not address_line_1 or not address_line_2 or not postal_code:
            change_address = True
            if full_name is None or full_name == '':
                messages.success(request, '수령인 이름이 입력되지 않았습니다.')
            elif phone_number is None or phone_number == '':
                messages.success(request, '전화번호가 입력되지 않았습니다.')
            elif address_line_1 is None or address_line_1 == '':
                messages.success(request, '주소가 입력되지 않았습니다.')
            elif address_line_2 is None or address_line_2 == '':
                print('address_line_2',address_line_2)
                messages.success(request, '상세주소가 입력되지 않았습니다.')
            elif postal_code is None or postal_code == '':
                messages.success(request, '우편번호가 입력되지 않았습니다.')
            # return render(request, "carts/checkout-iamport.html", context)
            # return redirect("carts:checkout-iamport")
        elif not shipping_address_obj:
            shipping_address_obj = Address.objects.create(billing_profile=billing_profile,
                                                            address_type='shipping', 
                                                            full_name=full_name,
                                                            email=email,
                                                            phone_number=phone_number,
                                                            address_line_1=address_line_1,
                                                            address_line_2=address_line_2,
                                                            postal_code=postal_code
                                                            )
            billing_address_obj = Address.objects.create(billing_profile=billing_profile,
                                                            address_type='billing', 
                                                            full_name=full_name,
                                                            email=email,
                                                            phone_number=phone_number,
                                                            address_line_1=address_line_1,
                                                            address_line_2=address_line_2,
                                                            postal_code=postal_code
                                                            )
            # address_changed = True
            # point_changed = False
            change_address = False
            print("Address created.")
            messages.success(request, "배송지 정보가 만들어졌습니다.")
        else:
            shipping_address_obj.full_name = full_name
            shipping_address_obj.email = email
            shipping_address_obj.phone_number = phone_number
            shipping_address_obj.address_line_1 = address_line_1
            shipping_address_obj.address_line_2 = address_line_2
            shipping_address_obj.postal_code = postal_code
            
            shipping_address_obj.save()
            change_address = False # 주소변경 완료됐으므로 템플릿에 체인지 하자 안해도됨.
            print("Address changed")
            messages.success(request, "배송지 정보가 수정되었습니다.")

        
        context = {
            'billing_profile': billing_profile,
            'shipping_address_obj': shipping_address_obj,
            'billing_address_obj': billing_address_obj,
            'address_qs': address_qs,
            # 'address_changed': address_changed,
            'change_address': change_address,
            

            }
        return render(request, "addresses/change_address.html", context)
    elif request.method == 'POST' and post_purpose == 'modify_address':
        context = {
            'billing_profile': billing_profile,
            'shipping_address_obj': shipping_address_obj,
            'billing_address_obj': billing_address_obj,
            'address_qs': address_qs,
            # 'address_changed': address_changed,
            'change_address': True,

            }
        return render(request, "addresses/change_address.html", context)    
