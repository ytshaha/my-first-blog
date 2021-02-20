from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
    )


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email and username:
            raise ValueError("Users must have an username and an email address.")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name
        )
        user_obj.username = username
        user_obj.email = email
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True) # can login
    staff = models.BooleanField(default=False) # staff user non superuser
    admin = models.BooleanField(default=False) # superuser
    timestamp = models.DateTimeField(auto_now_add=True)
    # confirm = models.BooleanField(default=False)
    # confirmed_date = models.DateTimeField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

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

    @property
    def is_active(self):
        return self.active

# class Profile(models.Model):
#     user = models.OneToOneField(User)


class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email