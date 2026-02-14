"""
Tests for horoscope/tasks/messaging.py — send_message and send_messages_batch.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSendMessage:
    @pytest.mark.django_db
    def test_send_message_success(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_message(telegram_uid=12345, text="Hello")

        assert result is True
        mock_app_context.send_message.assert_called_once_with(
            text="Hello",
            reply_markup=None,
        )
        mock_bot.session.close.assert_called_once()

    @pytest.mark.django_db
    def test_send_message_with_reply_markup(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()
        mock_keyboard = MagicMock()

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_message(
                telegram_uid=12345,
                text="Hello",
                reply_markup=mock_keyboard,
            )

        assert result is True
        mock_app_context.send_message.assert_called_once_with(
            text="Hello",
            reply_markup=mock_keyboard,
        )

    @pytest.mark.django_db
    def test_send_message_failure(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock(side_effect=Exception("Telegram API error"))

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_message(telegram_uid=12345, text="Hello")

        assert result is False
        mock_bot.session.close.assert_called_once()

    @pytest.mark.django_db
    def test_send_message_closes_session_on_failure(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock(side_effect=RuntimeError("Connection lost"))

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_message(telegram_uid=99999, text="Test")

        assert result is False
        mock_bot.session.close.assert_called_once()


class TestSendMessagesBatch:
    @pytest.mark.django_db
    def test_send_batch_all_success(self):
        from horoscope.tasks.messaging import send_messages_batch

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        messages = [
            (111, "Hello user 1", None),
            (222, "Hello user 2", None),
            (333, "Hello user 3", None),
        ]

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_messages_batch(messages)

        assert result == 3
        assert mock_app_context.send_message.call_count == 3
        mock_bot.session.close.assert_called_once()

    @pytest.mark.django_db
    def test_send_batch_partial_failures(self):
        from horoscope.tasks.messaging import send_messages_batch

        call_count = 0

        async def _side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Failed for user 2")

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock(side_effect=_side_effect)

        messages = [
            (111, "Hello user 1", None),
            (222, "Hello user 2", None),
            (333, "Hello user 3", None),
        ]

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_messages_batch(messages)

        assert result == 2
        mock_bot.session.close.assert_called_once()

    @pytest.mark.django_db
    def test_send_batch_empty_list(self):
        from horoscope.tasks.messaging import send_messages_batch

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user'):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_messages_batch([])

        assert result == 0
        mock_bot.session.close.assert_called_once()

    @pytest.mark.django_db
    def test_send_batch_with_keyboards(self):
        from horoscope.tasks.messaging import send_messages_batch

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()
        mock_keyboard = MagicMock()

        messages = [
            (111, "Hello", mock_keyboard),
        ]

        with patch('aiogram.Bot') as MockBot, \
             patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            mock_bot = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            result = send_messages_batch(messages)

        assert result == 1
        mock_app_context.send_message.assert_called_once_with(
            text="Hello",
            reply_markup=mock_keyboard,
        )
