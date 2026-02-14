from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update
from django.conf import settings
from django.utils import translation


class UserLanguageMiddleware(BaseMiddleware):
    """
    Middleware that activates Django's translation for the user's Telegram language.

    Maps Telegram language_code to supported locales and activates Django's
    translation context so that gettext_lazy strings resolve correctly.
    Falls back to Django's LANGUAGE_CODE if the user's language is not supported.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_obj = None
        if isinstance(event, Message):
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery):
            user_obj = event.from_user
        elif isinstance(event, Update):
            if event.message:
                user_obj = event.message.from_user
            elif event.callback_query:
                user_obj = event.callback_query.from_user

        locale = settings.LANGUAGE_CODE
        if user_obj and user_obj.language_code:
            lang_code = user_obj.language_code.lower().split('-')[0]
            if lang_code in settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES:
                locale = lang_code

        translation.activate(locale)
        try:
            return await handler(event, data)
        finally:
            translation.deactivate()
