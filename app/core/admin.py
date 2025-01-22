from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core.models import User


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (
            None, {
                'fields': ['name', 'email', 'password']
            }
        ),
        (
            _('Permissions'), {
                'fields': ['is_active', 'is_staff', 'is_superuser']
            }
        ),
        (_('Important dates'), {'fields': ['last_login']}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = [
        (None, {
            'classes': ('wide',),
            'fields': [
                'name',
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser'
            ]
        }),
    ]


admin.site.register(User, UserAdmin)
