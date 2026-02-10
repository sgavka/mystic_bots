from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from horoscope import callbacks


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⭐ Subscribe for full horoscope",
            callback_data=callbacks.SUBSCRIBE,
        )]
    ])
