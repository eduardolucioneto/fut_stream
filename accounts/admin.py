from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_premium', 'can_create_stream', 'can_delete_stream', 'is_active')
    list_editable = ('is_staff', 'is_superuser', 'is_premium', 'can_create_stream', 'can_delete_stream')
    # Extend the default fieldsets to include the custom is_premium field
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Permissões de Stream', {'fields': ('is_premium', 'can_create_stream', 'can_delete_stream')}),
    )
