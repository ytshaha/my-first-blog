from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm


from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import EmailActivation, GuestEmail, RegisterTicket
from .signals import user_logged_in


User = get_user_model()

class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("register")
            msg = '''This email does not exists, would you like to register?
            Would you like to <a href="{link}">register</a>?
            '''.format(link=register_link)
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','email','full_name', 'phone_number')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField(label='이름', required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    phoe_number = forms.CharField(label='전화번호', required=False, widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ['full_name', 'phoe_number']

class PasswordChangeForm(PasswordChangeForm):
    password1 = forms.CharField(label='비밀번호', required=True, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='비밀번호 확인', required=True, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ['password1', 'password2']


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username','email', 'full_name', 'phone_number', 'password', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
    

class GuestForm(forms.ModelForm):
    # email = forms.EmailField() 
    class Meta:
        model = GuestEmail
        fields = [
            'email'
        ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super(GuestForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session['guest_email_id'] = obj.id

        return obj
    

class LoginForm(forms.Form):
    username = forms.CharField(label='ID')
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        username  = data.get("username")
        password  = data.get("password")
        try:
            email = User.objects.get(username=username).email
        except:
            email = None    
        qs = User.objects.filter(username=username)
        if qs.exists():
            # user email is registered, check active.
            not_active = qs.filter(is_active=False)
            if not_active.exists():
                # not active, check email activation
                link = reverse("accounts:resend-activation")
                reconfirm_mgs = """Go to <a href='{resend_link}'>
                resend confirmation email</a>
                """.format(resend_link=link)
                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    msg1 = 'Please check your email to confirm your account.' + reconfirm_mgs
                    raise forms.ValidationError(mark_safe(msg1))
                email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
                if email_confirm_exists:
                    msg2 = "Email not confirmed." + reconfirm_mgs
                    raise forms.ValidationError(mark_safe(msg2))
                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError("This user is inactive")



        user = authenticate(request, username=username, password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")
        login(request, user)
        self.user = user
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            del request.session['guest_email_id']
        except:
            pass
        return data


    # def form_valid(self, form):
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
        
    #     username  = form.cleaned_data.get("username")
    #     password  = form.cleaned_data.get("password")
        
    #     if user is not None:
    #         if not user.is_active:
    #             # message
    #             messages.error(request, "This user in inactive")
    #             return super(LoginView, self).form_valid(form)
    #         login(request, user)
    #         try:
    #             del request.session['guest_email_id']
    #         except:
    #             pass
    #         if is_safe_url(redirect_path, request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect("shop:index")
    #     return super(LoginView, self).form_valid(form
        # obj = EmailActivation.create(user=instance))

class RegisterForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='*비밀번호', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='*비밀번호 확인', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True
            if field_name == 'username':
                field.min_length = 4

    class Meta:
        model = User
        fields = ('username','email','full_name', 'phone_number')
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control'}),
            # 'password1': forms.PasswordInput(attrs={'class':'form-control'}),
            # 'password2': forms.PasswordInput(attrs={'class':'form-control'}),
        }
        labels = {
            'username':  ('*ID'),
            'email':  ('*이메일주소'),
            'full_name':  ('*이름'),
            'phone_number':  ('*전화번호'),
            'password1':  ('*비밀번호'),
            'password2':  ('*비밀번호 확인'),
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("패스워드가 일치하지 않습니다.")
        if len(password1) < 8:
            raise forms.ValidationError("패스워드가 너무 짧습니다.(8글자이상)")
            
        return password2
    
    def clean(self):
        cleaned_data = super().clean()
        print('cleaned_data',cleaned_data)
        # username = cleaned_data.get('username')
        # email = cleaned_data.get('email')
        # phone_number = cleaned_data.get('phone_number')
        # full_name = cleaned_data.get('full_name')
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False # send confirmation email via signals
        # obj.send_activation()
        if commit:
            user.save()
        return user

    
class RegisterTicketForm(forms.ModelForm):
    ticket_number = forms.CharField(label='*가입티켓 번호', max_length=50, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    key = forms.CharField(label='*가입티켓 키', max_length=50, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))


    class Meta:
        model = RegisterTicket
        fields = ('ticket_number', 'key',)

    def clean_register_ticket(self):
        # Check that the two password entries match
        print('clean_register_ticket소환')
        ticket_number = self.cleaned_data.get("ticket_number")
        key = self.cleaned_data.get("key")
        register_ticket_qs = RegisterTicket.objects.filter(ticket_number=ticket_number)
        if register_ticket_qs.count() == 1:
            register_ticket_obj = register_ticket_qs.first()
            if register_ticket_obj.key == key:
                return key
            else:
                raise forms.ValidationError("키가 옳바르지 않습니다.")
        else:
            raise forms.ValidationError("가입티켓번호가 틀립니다.")


# class RegisterForm(forms.Form):
#     username = forms.CharField()
#     email = forms.EmailField() 
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         qs = User.objects.filter(username=username)
#         if qs.exists():
#             raise forms.ValidationError("Username is taken")
#         return username 
    
#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             raise forms.ValidationError("Email is taken")
#         return eamil

#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password2 != password:
#             raise forms.ValidationError("Passwords must match")
#         return data