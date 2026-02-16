from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from horoscope.callbacks import LanguageCallback, SkipBirthTimeCallback, SubscribeCallback
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
