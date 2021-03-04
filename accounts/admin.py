from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import GuestEmail,EmailActivation
from .forms import UserAdminCreationForm, UserAdminChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username','email', 'full_name', 'phone_number', 'admin')
    list_filter = ('admin','staff',)
    fieldsets = (
        (None, {'fields': ('username','email', 'password')}),
        ('Details', {'fields': ('full_name', 'phone_number',)}),
        ('Permissions', {'fields': ('admin','staff','is_active',)}),
        ('Points', {'fields': ('points',)}),
        
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email','full_name', 'phone_number',)
    ordering = ('username','email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
# admin.site.register(Group)

class EmailActivationAdmin(admin.ModelAdmin):
    serarch_fields = ['email']
    class Meta:
        model = EmailActivation

admin.site.register(EmailActivation, EmailActivationAdmin)

class GuestEmailAdmin(admin.ModelAdmin):
    serarch_fields = ['email']
    class Meta:
        model = GuestEmail

admin.site.register(GuestEmail, GuestEmailAdmin)