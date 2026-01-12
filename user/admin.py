from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User, Payment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для кастомной модели User"""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Поля для отображения при редактировании пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Поля при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка для модели Payment"""
    list_display = ('user', 'amount', 'payment_method', 'payment_date', 'paid_course', 'paid_lesson')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('payment_date',)
