from aiogram.filters.callback_data import CallbackData


class SubscribeCallback(CallbackData, prefix="subscribe"):
    pass


class LanguageCallback(CallbackData, prefix="lang"):
    code: str


class SkipBirthTimeCallback(CallbackData, prefix="skip_birth_time"):
    pass


class TimezoneCallback(CallbackData, prefix="tz"):
    offset: int


class NotificationHourCallback(CallbackData, prefix="notif_hour"):
    hour: int


class ResetNotificationHourCallback(CallbackData, prefix="reset_notif"):
    pass
