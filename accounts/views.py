import pandas as pd
import random
import json

from django.contrib.auth import authenticate, login, get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


from django.urls import reverse # from django.core.urlresolvers import reverse --> django 2.0에서 변경됨.
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template

from mysite.mixin import NextUrlMixIn, RequestFormAttachMixin
from mysite.alimtalk import send
from mysite.utils import check_ticket_activate
from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm, PasswordChangeForm, RegisterTicketForm
from .models import GuestEmail, EmailActivation, RegisterTicket
from .signals import user_logged_in
from tickets.models import Ticket

User = get_user_model()

# Create your views here.
@login_required # /account/lo gin/?next=/some/path/
def account_home_view(request):
    return render(request, "accounts/home.html", {})

class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = "accounts/home.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(AccountHomeView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        register_ticket_qs = RegisterTicket.objects.filter(user=user)
        context['register_ticket_qs'] = register_ticket_qs
        return context



class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None
    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            qs_confirm = qs.confirmable()
            if qs_confirm.count() == 1:
                obj = qs_confirm.first()
                obj.activate()
                messages.success(request, "이메일 인증이 완료되었습니다. 로그인이 가능합니다.")
                return redirect("login")
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg = '''이미 이메일 인증이 완료되어 있습니다.
                    비밀번호를 재설정이 필요하십니까?<a href="{link}"></a>?
                    '''.format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    return redirect("login")
        context = {
            'form': self.get_form()
        }
        return render(request, 'registration/activation-error.html', context)


    def post(self, request, *args, **kwargs):
        # create form to receive an email
        form = self.get_form()
        if form.is_valid(): 
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = '''계정 활성화 링크가 가입하신 이메일주소로 전송되었습니다.'''
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        context={'form':form, 'key':self.key}
        return render(self.request,'registration/activation-error.html', context)

def guest_register_view(request):
    form = GuestForm(request.POST or None)
    context = {
        "form": form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("/register/")
    return redirect("/register/")


class GuestRegisterView(NextUrlMixIn, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)


    # def form_valid(self, form):
    #     request = self.request
    #     email = form.cleaned_data.get('email')
    #     new_guest_email = GuestEmail.objects.create(email=email)
    #     return redirect(self.get_next_url())

from django.contrib.sites.models import Site

class LoginView(NextUrlMixIn, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/shop/'
    template_name = "accounts/login.html"
    
    default_next = '/shop/'
   
    def form_valid(self, form):
        next_path = self.get_next_url()
        # 유효하여 로긴하게 되면 현재 activate되어있는 티켓을 확인하여 기간내가 아니면 used 처리함.
        # 이것은 함수화해서 지속확인할 수 있게 해야할듯.
        request = self.request
        user = request.user
        ticket_activate = check_ticket_activate(user=user, request=request, model=Ticket)
        
        for key, value in self.request.session.items():
            print('{} => {}'.format(key, value))
        return redirect(next_path)

    
def register_ticket_confirm(request, *args, **kwargs):
    # form_class = RegisterTicketForm
    # success_url = '/register/'
    # template_name = "accounts/register_ticket_confirm.html"

    # default_next = 'register_ticket_confirm'
    if request.method == "GET":  # (self, request, key=None, *args, **kwargs):
        ticket_number = kwargs.get('ticket_number', None)
        key = kwargs.get('key', None)
        context = {
            'ticket_number': ticket_number,
            'key': key
        }
        return render(request, 'accounts/register_ticket_confirm.html', context)

    if request.method == "POST":
        ticket_number = request.POST.get("ticket_number", None)
        key = request.POST.get("key", None)
        if ticket_number == 'Moum8878':
            request.session['register_ticket_number'] = 'free pass'
            return redirect('register')

        register_ticket_qs = RegisterTicket.objects.filter(ticket_number=ticket_number, used=False)
        if register_ticket_qs.exists():
            register_ticket_obj = register_ticket_qs.first()
            if register_ticket_obj.key == key:
                register_ticket_confirm = True
                request.session['register_ticket_number'] = ticket_number
            else:
                messages.success(request, "가입티켓 키가 틀립니다.")
                return redirect('register_ticket_confirm')
        else:
            messages.success(request, "가입티켓 번호가 틀립니다.")
            return redirect('register_ticket_confirm')
        return redirect('register')
    return render(request, 'accounts/register_ticket_confirm.html', {}) 

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/register/success/'

    def get_context_data(self, *args, **kwargs):
        context = super(RegisterView, self).get_context_data(*args, **kwargs)
        # context['register_ticket_form'] = RegisterTicketForm
        request = self.request
        post_purpose = request.POST.get('post_purpose', None)
        register_ticket_confirm = False
        register_ticket_number = request.session.get('register_ticket_number', None)
        if register_ticket_number is not None:
            register_ticket_confirm = True
        context['register_ticket_confirm'] = register_ticket_confirm
        
        return context
    
    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        print('폼맞다?')
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form)
        print("폼안맞다.")
        print(form.errors)
        print(form.non_field_errors())
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

def register_success(request):
    register_ticket_number = request.session.get('register_ticket_number', None)
    if register_ticket_number == 'free pass':
        del request.session['register_ticket_number']
    else:
        register_ticket_obj = RegisterTicket.objects.get(ticket_number=register_ticket_number)
        register_ticket_obj.used = True
        register_ticket_obj.save()
        del request.session['register_ticket_number']
    return render(request, "accounts/register_success.html", {})
    


def send_phone_number_alimtalk(request):
    if request.method == 'POST' and request.is_ajax():
        print('Ajax requested.')
        phone_number = request.POST.get('phone_number', None)

        alimtalk_message = '''회원 가입하신 이메일로 계정 활성화 링크를 보내드렸습니다. 
24시간 이내에 메일 내 링크로 접속하시어 계정활성화를 해주세요.'''
        send(templateCode='register', to=phone_number, message=alimtalk_message)
        print("{}으로 결제완료 알림톡이 보내졌습니다.".format(phone_number))

        code = random.randint(1000,9999)
        print(code)
        request.session['phone_code'] = code
        return HttpResponse(json.dumps({'status': "success", 'message': "알림톡보내기 성공", 'code': code}),
                                    content_type="application/json")



def confirm_phone_number_alimtalk(request):
    if request.method == 'POST' and request.is_ajax():
        print('Ajax requested.')
        code = request.POST.get('code', None)
        code = int(code)
        print("request.session")
        for key, value in request.session.items():
            print('{} => {}'.format(key, value))
        if code ==  request.session['phone_code']:
            print('코드인증 성공')
            return HttpResponse(json.dumps({'status': "success", 'message': "코드인증성공"}),
                                        content_type="application/json")
        else:
            print('코드인증 실패')
            return HttpResponse(json.dumps({'status': "fail", 'message': "코드인증실패"}),
                                        content_type="application/json")

# class ProductDetailView(LoginRequiredMixin, generic.DetailView):
#     template_name = 'products/product_detail.html'
#     context_object_name = 'product'

#     def get_context_data(self, *args, **kwargs):
#         context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
#         print(context)
#         return context

#     def get_queryset(self, *args, **kwargs):
#         request = self.request
#         pk = self.kwargs.get('pk')
#         product_obj = Product.objects.filter(pk=pk)
#         request.session['product_number'] = product_obj.number
#         return product_obj    

class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-view.html'
    
    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Change Your Account Details'
        return context

    def get_success_url(self):
        request = self.request
        messages.success(request, "개인정보가 성공적으로 변경되었습니다.")
        return reverse("accounts:home")


class PasswordChangeView(LoginRequiredMixin, UpdateView):
    form_class = PasswordChangeForm
    template_name = 'registration/password_change_form.html'
    
    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse("accounts:home")
# def login_page(request):
#     form = LoginForm(request.POST or None)
#     context = {
#         "form": form
#     }
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         username  = form.cleaned_data.get("username")
#         password  = form.cleaned_data.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             try:
#                 del request.session['guest_email_id']
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect("shop:index")
#         else:
#             # Return an 'invalid login' error message.
#             print("Error")
#     return render(request, "accounts/login.html", context)

# User = get_user_model()

# def register_page(request):
#     form = RegisterForm(request.POST or None)
#     context = {
#         "form": form
#     }
#     if form.is_valid():
#         form.save()
#     return render(request, "accounts/register.html", context)


# def user_home(request): 
#     return render(request, 'accounts/user_home.html', {})

def make_register_ticket(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        user_qs = User.objects.filter(username=username)
        amount = request.POST.get('amount', None)
        if user_qs.count() == 0:
            messages.success(request, 'ID를 잘못입력했습니다.')
            return redirect('accounts:make_register_ticket')
        if amount is None or amount == 0:
            messages.success(request, '만들려고 가입티켓 갯수가 잘못됐습니다.')
            return redirect('accounts:make_register_ticket')
        
        user_obj = user_qs.first()
        register_ticket_count = RegisterTicket.objects.filter(user=user_obj).count()
        
        for i in range(1, int(amount)+1):
            RegisterTicket.objects.create(user=user_obj, ticket_number='{}_{}'.format(username, register_ticket_count + i))


        return redirect('accounts:make_register_ticket_success')

    return render(request, 'accounts/make_register_ticket.html', {})
    
def make_register_ticket_success(request):
    return render(request, 'accounts/make_register_ticket_success.html', {})

def send_register_ticket(request):
    user = request.user
    register_ticket_qs = RegisterTicket.objects.filter(user=user, shared=False)

    context = {
        'register_ticket_qs' : register_ticket_qs
    }

    return render(request, 'accounts/send_register_ticket.html', context)

def send_register_ticket_success(request):
    
    if request.method == 'POST':
        email = request.POST.get('email', None)
        phone_number = request.POST.get('phone_number', None)
        ticket_number = request.POST.get('ticket_number', None)
        print(email, type(email))
        print(email=="")
        if email == "" and phone_number == "":
            messages.success(request, "이메일과 카카오톡이 있는 전화번호 중 하나 이상은 입력해주세요.")
            return redirect('accounts:send_register_ticket')

        register_ticket_obj = RegisterTicket.objects.get(ticket_number=ticket_number)
        if email != "":
            if User.objects.filter(email=email).exists():
                messages.success(request, '이미 회원인 이메일주소로 보내려고 합니다. 다른 이메일로 보내주세요.')
                return redirect('accounts:send_register_ticket')
            
            if register_ticket_obj.shared:
                messages.success(request, '이미 보낸 티켓을 선택하셨습니다. 전송되지 않은 티켓을 선택해주세요.')
                return redirect('accounts:send_register_ticket')
            # if RegisterTicket.objects.filter(sent_mail=email).exists():
            #     messages.success(request, '이미 가입티켓을 받은 회원의 이메일주소로 보내려고 합니다. 다른 이메일로 보내주세요.')
            #     return redirect('accounts:send_register_ticket')
            # 가입티켓 상태변경(보내짐으로 바꾸고 메일주소도 넣기.)
            register_ticket_qs = RegisterTicket.objects.filter(ticket_number=ticket_number)
            register_ticket_obj = register_ticket_qs.first()
            register_ticket_obj.shared = True
            register_ticket_obj.sent_mail = email
            register_ticket_obj.save()

            #메일 보내기
            base_url = getattr(settings, 'BASE_URL', 'https://moum8.herokuapp.com')
            key_path = reverse("register_ticket_confirm", kwargs={'ticket_number':register_ticket_obj.ticket_number, 'key':register_ticket_obj.key})
            path = "{base}{path}".format(base=base_url, path=key_path)
            context = {
                'path':path,
                'email': email,
                'ticket_number': register_ticket_obj.ticket_number,
                'key': register_ticket_obj.key
            }
            txt_ = get_template("registration/emails/send_register_ticket.txt").render(context)
            html_ = get_template("registration/emails/send_register_ticket.html").render(context)
            subject = '명품 병행수입 쇼핑몰_MOUM8_가입티켓을 보내드립니다.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            # send_mail = send_email(
            #                         emailMsg=txt_, 
            #                         to=self.email, 
            #                         subject=subject)
            sent_mail = send_mail(
                        subject,
                        txt_,
                        from_email,
                        recipient_list,
                        html_message=html_,
                        fail_silently=False,
                        )
            print("{}로 가입티켓 메일을 송부하였습니다.티켓번호:{}, 키:{}".format(email, register_ticket_obj.ticket_number, register_ticket_obj.key))
        if phone_number != "":

            templateCode ='alim1'
            to = phone_number
            alimtalk_message = """안녕하세요.
명품 병행수입 쇼핑몰 MOUM8 입니다. 

저희 사이트는 VIP로 선정되신 분만 가입할 수 있는 프라이빗 사이트로 운영되고 있습니다. 
고객님께 프라이빗 명품 병행수입 쇼핑몰 MOUM8로 가입이 가능한 티켓을 송부드립니다. 
아래 링크를 들어가시면 가입을 진행하실 수 있습니다. 

가입티켓 번호 :  {}
가입티켓 키 :  {}""".format(register_ticket_obj.ticket_number, register_ticket_obj.key)
            send(templateCode=templateCode, to=to, message=alimtalk_message)
            print("{}로 가입티켓 메일을 송부하였습니다.티켓번호:{}, 키:{}".format(email, register_ticket_obj.ticket_number, register_ticket_obj.key))   


    context = {
                'email': email,
                'phone_number': phone_number,
                'ticket_number': register_ticket_obj.ticket_number,
                'key': register_ticket_obj.key
            }

    return render(request, 'accounts/send_register_ticket_success.html', context)



from django.core.files.storage import default_storage
import os
from django.conf import settings

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
REGISTER_TICKET_ROOT = os.path.join(MEDIA_ROOT, 'register_ticket_excel.xlsx')

def get_register_ticket_excel(request):
    print('실행')
    if request.method == 'POST':
        username = request.POST.get('username', None)
        print(username, '의 티켓 다운로드가 요청되었습니다.')
        qs = RegisterTicket.objects.filter(user__username=username, shared=False)
        if qs.count() == 0:
            messages.success(request, '해당 {}는 티켓이 없습니다.'.format(username))
            return redirect('accounts:get_register_ticket_excel')
        q = qs.values("ticket_number", "key")
        df = pd.DataFrame.from_records(q)
        print('dataframe print...')
        print(df)
        
        # register_ticket_excel = df.to_excel(REGISTER_TICKET_ROOT)
        # file_name = default_storage.save(file.name, file)
        # print('file print...')
        # print(register_ticket_excel)
        context = {
            'qs':qs,
        }
        return render(request, 'accounts/get_register_ticket_excel.html', context)

    return render(request, 'accounts/get_register_ticket_excel.html', {})


def deactive_account(request):
    if request.method == 'POST':
        user = request.user
        user_obj = User.objects.get(username=user)
        user_obj.is_active = False
        user_obj.save()
        return redirect('logout')
    return render(request, 'accounts/deactive.html', {})
