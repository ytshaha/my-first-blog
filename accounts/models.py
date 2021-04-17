from datetime import timedelta
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
    )
from django.db.models import Q

from django.urls import reverse # from django.core.urlresolvers import reverse --> django 2.0에서 변경됨.

from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import get_template
from mysite.utils import unique_key_generator, random_string_generator
# from mysite.gmail import send_email
# from mysite.gmail import get_credentials, create_message_and_send, create_message_without_attachment, create_Message_with_attachment, send_Message_without_attachement, send_Message_with_attachement
from points.models import Point

from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator, RegexValidator



# send_mail(subject, message, from_email, recipient_list, html_message)

username_length_validator = MinLengthValidator(4, "길이가 너무 짧습니다.(4글자이상)")
username_regex_validator = RegexValidator(
                                    regex='^(?=.{4,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$',
                                    message='''아이디가 유효하지 않습니다.  
                                    4~20자까지 가능합니다. 
                                    특수문자는 . _만 가능합니다. 
                                    특수문자로 끝나거나 시작할수 없습니다. 
                                    특수문자는 2번 연속 사용할 수 없습니다.''')

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)

class UserManager(BaseUserManager):
    def create_user(self, username, email, full_name, phone_number, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email and username:
            raise ValueError("Users must have an username and an email address.")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name,
            phone_number=phone_number
        )
        user_obj.username = username
        user_obj.email = email
        user_obj.phone_number = phone_number
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, full_name, phone_number, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, username, full_name, phone_number, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True, help_text='4~20글자 사이로 지정하십시오.', validators=[username_length_validator, username_regex_validator])
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    # active = models.BooleanField(default=True) # can login
    is_active = models.BooleanField(default=True) # can login
    staff = models.BooleanField(default=False) # staff user non superuser
    admin = models.BooleanField(default=False) # superuser
    timestamp = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    # confirm = models.BooleanField(default=False)
    # confirmed_date = models.DateTimeField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_email(self):
        return self.email
    
    def get_full_name(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    # @property
    # def is_active(self):
    #     return self.active

# class Profile(models.Model):
#     user = models.OneToOneField(User)

def post_save_point_total(sender, instance, created, *args, **kwargs):
    if created:
        point_obj = instance
        user = point_obj.user
        qs = User.objects.filter(username=user.username)
        
        user.points = user.points + point_obj.amount
        user.save()

post_save.connect(post_save_point_total, sender=Point)



class EmailActivationQuerySet(models.query.QuerySet): # EmailActivation.objects.all().confirmable()
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(
                activated=False,
                forced_expired=False
                ).filter(
                    timestamp__gt=start_range,
                    timestamp__lte=end_range
                )

class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)
    
    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        return self.get_queryset().filter(
                        Q(email=email) | Q(user__email=email)
                    ).filter(
                        activated=False
                    )

class EmailActivation(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    email           = models.EmailField()
    key             = models.CharField(max_length=120, blank=True, null=True)
    activated       = models.BooleanField(default=False)
    forced_expired  = models.BooleanField(default=False)
    expires         = models.IntegerField(default=7) # 7 days
    timestamp       = models.DateTimeField(auto_now_add=True)
    update          = models.DateTimeField(auto_now=True)
    
    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable() #1 object
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            user = self.user
            user.is_active = True
            user.save()
            self.activated = True
            self.save()
            return True
        return False



    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', 'https://moum8.com')
                key_path = reverse("accounts:email-activate", kwargs={'key':self.key}) # use reverse
                path = "{base}{path}".format(base=base_url, path=key_path)
                context = {
                    'path':path,
                    'email': self.email
                }
                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)
                subject = '명품 병행수입 쇼핑몰_MOUM8_가입 계정활성화 메일'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]

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
                return send_mail
        return False
        
def pre_save_email_activation(sender, instance, *args, **kwrags):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation, sender=EmailActivation)

def post_save_user_create_reciever(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation()

post_save.connect(post_save_user_create_reciever, sender=User)

class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class RegisterTicket(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)         # 일종의 추천인아이디
    ticket_number   = models.CharField(max_length=120, unique=True)             # 티켓 번호 추천인아이디+숫자.
    key             = models.CharField(max_length=120, blank=True, null=True)   # 티켓별 키
    sent_mail       = models.EmailField(blank=True, null=True)                                       # 해당 티켓을 보낸 메일. 한번보내면 이 이메일이외에는 더이상 못보냄.
    sent_alimtalk   = models.CharField(max_length=120, blank=True, null=True)
    shared          = models.BooleanField(default=False)                        # 메일로 공유됨
    used            = models.BooleanField(default=False)                        # 가입시 사용됨..
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_number
def pre_save_register_ticket(sender, instance, *args, **kwrags):
    if instance.key is None:
        instance.key = random_string_generator(size=20)

pre_save.connect(pre_save_register_ticket, sender=RegisterTicket)



# from uuid import uuid4
# from datetime import datetime

# def upload_register_ticket_path(instance, filename):
#     ymd_path = datetime.now().strftime('%Y/%m/%d')
#     uuid_name = uuid4().hex
#     return '/'.join(['register_ticket_excel/', ymd_path, uuid_name])


# class RegisterTicketExcel(models.Model):
#     file            = models.FileField(upload_to=upload_register_ticket_path, null=True, blank=True, verbose_name='파일')


