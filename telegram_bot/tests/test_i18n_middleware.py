"""Tests for UserLanguageMiddleware."""

from unittest.mock import MagicMock, patch

import pytest
from django.utils import translation

from telegram_bot.middlewares.i18n import UserLanguageMiddleware


def _make_message_event(language_code: str | None = "en") -> MagicMock:
    event = MagicMock()
    event.__class__ = type('Message', (), {})
    from aiogram.types import Message
    event.__class__ = Message
    user = MagicMock()
    user.language_code = language_code
    event.from_user = user
    return event


class TestUserLanguageMiddleware:

    @pytest.mark.asyncio
    async def test_activates_supported_language(self):
        middleware = UserLanguageMiddleware()
        event = _make_message_event(language_code="ru")

        activated_lang = None

        async def capture_handler(ev, data):
            nonlocal activated_lang
            activated_lang = translation.get_language()
            return None

        with patch('telegram_bot.middlewares.i18n.settings') as mock_settings:
            mock_settings.LANGUAGE_CODE = 'en'
            mock_settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk'}
            await middleware(capture_handler, event, {})

        assert activated_lang == 'ru'

    @pytest.mark.asyncio
    async def test_falls_back_to_default_for_unsupported(self):
        middleware = UserLanguageMiddleware()
        event = _make_message_event(language_code="ja")

        activated_lang = None

        async def capture_handler(ev, data):
            nonlocal activated_lang
            activated_lang = translation.get_language()
            return None

        with patch('telegram_bot.middlewares.i18n.settings') as mock_settings:
            mock_settings.LANGUAGE_CODE = 'en'
            mock_settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk'}
            await middleware(capture_handler, event, {})

        assert activated_lang == 'en'

    @pytest.mark.asyncio
    async def test_handles_none_language_code(self):
        middleware = UserLanguageMiddleware()
        event = _make_message_event(language_code=None)

        activated_lang = None

        async def capture_handler(ev, data):
            nonlocal activated_lang
            activated_lang = translation.get_language()
            return None

        with patch('telegram_bot.middlewares.i18n.settings') as mock_settings:
            mock_settings.LANGUAGE_CODE = 'en'
            mock_settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk'}
            await middleware(capture_handler, event, {})

        assert activated_lang == 'en'

    @pytest.mark.asyncio
    async def test_handles_language_with_region(self):
        middleware = UserLanguageMiddleware()
        event = _make_message_event(language_code="en-US")

        activated_lang = None

        async def capture_handler(ev, data):
            nonlocal activated_lang
            activated_lang = translation.get_language()
            return None

        with patch('telegram_bot.middlewares.i18n.settings') as mock_settings:
            mock_settings.LANGUAGE_CODE = 'en'
            mock_settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk'}
            await middleware(capture_handler, event, {})

        assert activated_lang == 'en'

    @pytest.mark.asyncio
    async def test_deactivates_after_handler(self):
        middleware = UserLanguageMiddleware()
        event = _make_message_event(language_code="ru")

        with patch('telegram_bot.middlewares.i18n.settings') as mock_settings:
            mock_settings.LANGUAGE_CODE = 'en'
            mock_settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk'}

            async def capture_handler(ev, data):
                return None

            await middleware(capture_handler, event, {})

        # After middleware completes, translation should be deactivated
        assert translation.get_language() is None or translation.get_language() == 'en'
