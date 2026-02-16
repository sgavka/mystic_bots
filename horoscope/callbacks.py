from aiogram.filters.callback_data import CallbackData


class SubscribeCallback(CallbackData, prefix="subscribe"):
    pass


class LanguageCallback(CallbackData, prefix="lang"):
    code: str


class SkipBirthTimeCallback(CallbackData, prefix="skip_birth_time"):
    pass
