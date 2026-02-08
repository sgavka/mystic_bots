from django.contrib import admin
from django.utils.html import format_html

from horoscope.models import Horoscope, Subscription, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_telegram_uid', 'name', 'date_of_birth', 'place_of_living', 'created_at')
    list_filter = ('date_of_birth',)
    search_fields = ('user_telegram_uid', 'name', 'place_of_birth', 'place_of_living')
    readonly_fields = ('user_telegram_uid', 'created_at', 'updated_at')


@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_telegram_uid', 'horoscope_type', 'date', 'created_at')
    list_filter = ('horoscope_type', 'date')
    search_fields = ('user_telegram_uid',)
    readonly_fields = ('id', 'user_telegram_uid', 'horoscope_type', 'date', 'full_text', 'teaser_text', 'created_at')

    def full_text_preview(self, obj):
        if obj.full_text and len(obj.full_text) > 200:
            return format_html('<pre>{}</pre>', obj.full_text[:200] + '...')
        return format_html('<pre>{}</pre>', obj.full_text or '')
    full_text_preview.short_description = 'Full text (preview)'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_telegram_uid', 'status', 'started_at', 'expires_at', 'reminder_sent_at')
    list_filter = ('status',)
    search_fields = ('user_telegram_uid',)
    readonly_fields = ('id', 'user_telegram_uid', 'started_at', 'created_at', 'updated_at')
