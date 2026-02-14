"""
Internationalization (i18n) middleware for Telegram bot using aiogram's built-in I18n
"""
from pathlib import Path
from typing import Any

from aiogram.utils.i18n import I18n, I18nMiddleware
from aiogram.types import TelegramObject, User


SUPPORTED_LOCALES = ("en", "ru", "uk")
DEFAULT_LOCALE = "en"

LOCALES_PATH = Path(__file__).parent.parent.parent / "locale"

# Global I18n instance
i18n = I18n(path=LOCALES_PATH, default_locale=DEFAULT_LOCALE, domain="messages")


class UserLanguageMiddleware(I18nMiddleware):
    """
    Middleware that determines user language from Telegram user data.
    Falls back to default locale if user language is not supported.
    """

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        """
        Get locale from user's Telegram language_code.
        Falls back to 'en' if the language is not supported.
        """
        user: User | None = data.get("event_from_user")
        if user and user.language_code:
            # Map Telegram language codes to our supported locales
            lang_code = user.language_code.lower()

            # Direct mapping for supported languages
            if lang_code in SUPPORTED_LOCALES:
                return lang_code

            # Handle language variants (e.g., 'en-US' -> 'en')
            base_lang = lang_code.split("-")[0]
            if base_lang in SUPPORTED_LOCALES:
                return base_lang

        return DEFAULT_LOCALE


def create_i18n_middleware() -> UserLanguageMiddleware:
    """
    Create and configure the i18n middleware.

    Returns:
        Configured UserLanguageMiddleware instance
    """
    return UserLanguageMiddleware(i18n=i18n)
