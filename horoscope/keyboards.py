from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from horoscope.callbacks import (
    LanguageCallback,
    NotificationHourCallback,
    ResetNotificationHourCallback,
    SkipBirthTimeCallback,
    SubscribeCallback,
    TimezoneCallback,
)
from horoscope.utils import translate

KEYBOARD_SUBSCRIBE = _("⭐ Subscribe for full horoscope")


def language_keyboard(current_language: str | None = None) -> InlineKeyboardMarkup:
    buttons = []
    for lang_code, lang_name in settings.HOROSCOPE_LANGUAGE_NAMES.items():
        flag = settings.HOROSCOPE_LANGUAGE_FLAGS.get(lang_code, '')
        label = f"{flag} {lang_name}"
        if current_language and lang_code == current_language:
            label += " ✓"
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=LanguageCallback(code=lang_code).pack(),
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


KEYBOARD_SKIP_BIRTH_TIME = _("⏭ Skip")


def skip_birth_time_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=translate(KEYBOARD_SKIP_BIRTH_TIME, language),
            callback_data=SkipBirthTimeCallback().pack(),
        )]
    ])


def subscribe_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=translate(KEYBOARD_SUBSCRIBE, language),
            callback_data=SubscribeCallback().pack(),
        )]
    ])


KEYBOARD_RESET_TO_DEFAULT = _("🔄 Reset to language default")


def timezone_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with common UTC offsets for timezone selection."""
    offsets = [
        (-12, "UTC-12"), (-11, "UTC-11"), (-10, "UTC-10"), (-9, "UTC-9"),
        (-8, "UTC-8"), (-7, "UTC-7"), (-6, "UTC-6"), (-5, "UTC-5"),
        (-4, "UTC-4"), (-3, "UTC-3"), (-2, "UTC-2"), (-1, "UTC-1"),
        (0, "UTC+0"), (1, "UTC+1"), (2, "UTC+2"), (3, "UTC+3"),
        (4, "UTC+4"), (5, "UTC+5"), (6, "UTC+6"), (7, "UTC+7"),
        (8, "UTC+8"), (9, "UTC+9"), (10, "UTC+10"), (11, "UTC+11"),
        (12, "UTC+12"), (13, "UTC+13"), (14, "UTC+14"),
    ]
    rows = []
    row = []
    for offset_val, label in offsets:
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=TimezoneCallback(offset=offset_val).pack(),
        ))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def notification_hour_keyboard(
    language: str = 'en',
    user_timezone_offset: int = 0,
) -> InlineKeyboardMarkup:
    """Keyboard with hours (in user's local time) for notification time selection."""
    rows = []
    row = []
    for local_hour in range(24):
        row.append(InlineKeyboardButton(
            text=f"{local_hour:02d}:00",
            callback_data=NotificationHourCallback(hour=local_hour).pack(),
        ))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(
        text=translate(KEYBOARD_RESET_TO_DEFAULT, language),
        callback_data=ResetNotificationHourCallback().pack(),
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)
