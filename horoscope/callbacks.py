from aiogram.filters.callback_data import CallbackData


class SubscribeCallback(CallbackData, prefix="subscribe"):
    pass


class LanguageCallback(CallbackData, prefix="lang"):
    code: str
