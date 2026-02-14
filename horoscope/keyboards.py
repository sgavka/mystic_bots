from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from horoscope import callbacks
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
            callback_data=f"{callbacks.LANGUAGE_PREFIX}{lang_code}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscribe_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=translate(KEYBOARD_SUBSCRIBE, language),
            callback_data=callbacks.SUBSCRIBE,
        )]
    ])


