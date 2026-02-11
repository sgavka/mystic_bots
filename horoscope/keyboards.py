from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from horoscope import callbacks
from horoscope.translations import LANGUAGE_FLAGS, LANGUAGE_NAMES, t


def language_keyboard(current_language: str | None = None) -> InlineKeyboardMarkup:
    buttons = []
    for lang_code, lang_name in LANGUAGE_NAMES.items():
        flag = LANGUAGE_FLAGS.get(lang_code, '')
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
            text=t("keyboard.subscribe", language),
            callback_data=callbacks.SUBSCRIBE,
        )]
    ])
