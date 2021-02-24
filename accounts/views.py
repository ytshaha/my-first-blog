from django.contrib.auth import authenticate, login, get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


from django.urls import reverse # from django.core.urlresolvers import reverse --> django 2.0에서 변경됨.
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe

from mysite.mixin import NextUrlMixIn, RequestFormAttachMixin
from mysite.utils import check_ticket_activate
from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import GuestEmail, EmailActivation
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
                messages.success(request, "Your email has been confirmed, Please login.")
                return redirect("login")
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg = '''Your email has already been confirmed.
                    Do you need to <a href="{link}">reset your password</a>?
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
        msg = '''Activation link sent, please check you email.'''
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
def check_ticket_activate(user, request, model):
    if user is not None:
        ticket_qs = model.objects.filter(user=user, status='activate')
        if ticket_qs.count() == 1:
            ticket_obj = ticket_qs.first()
            if ticket_obj.timestamp + timezone.timedelta(days=1) < timezone.now():
                ticket_obj.status = 'used'
                request.session['ticket_activate'] = False
                return True
            elif ticket_obj.timestamp + timezone.timedelta(days=1) >= timezone.now():
                request.session['ticket_activate'] = True
                return False
    return False

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

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/register/success/'

def register_success(request):
    return render(request, "accounts/register_success.html", {})
    
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