from django.contrib import admin

from core.models import Setting, User


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'value', 'updated_at')
    list_filter = ('type',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_uid', 'username', 'first_name', 'last_name', 'language_code', 'is_premium')
    list_filter = ('is_premium', 'language_code')
    search_fields = ('telegram_uid', 'username', 'first_name', 'last_name')
    readonly_fields = ('telegram_uid',)
