"""
Tests for horoscope/tasks/messaging.py — send_message and send_messages_batch.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSendMessage:
    @pytest.mark.django_db
    async def test_send_message_success(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        mock_bot = MagicMock()

        with patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            result = await send_message(
                bot=mock_bot,
                telegram_uid=12345,
                text="Hello",
            )

        assert result is True
        mock_app_context.send_message.assert_called_once_with(
            text="Hello",
            reply_markup=None,
        )

    @pytest.mark.django_db
    async def test_send_message_with_reply_markup(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()
        mock_keyboard = MagicMock()
        mock_bot = MagicMock()

        with patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            result = await send_message(
                bot=mock_bot,
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
    async def test_send_message_failure(self):
        from horoscope.tasks.messaging import send_message

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock(side_effect=Exception("Telegram API error"))
        mock_bot = MagicMock()

        with patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            result = await send_message(
                bot=mock_bot,
                telegram_uid=12345,
                text="Hello",
            )

        assert result is False


class TestSendMessagesBatch:
    @pytest.mark.django_db
    async def test_send_batch_all_success(self):
        from horoscope.tasks.messaging import send_messages_batch

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()
        mock_bot = MagicMock()

        messages = [
            (111, "Hello user 1", None),
            (222, "Hello user 2", None),
            (333, "Hello user 3", None),
        ]

        with patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            result = await send_messages_batch(bot=mock_bot, messages=messages)

        assert result == 3
        assert mock_app_context.send_message.call_count == 3

    @pytest.mark.django_db
    async def test_send_batch_partial_failures(self):
        from horoscope.tasks.messaging import send_messages_batch

        call_count = 0

        async def _side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Failed for user 2")

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock(side_effect=_side_effect)
        mock_bot = MagicMock()

        messages = [
            (111, "Hello user 1", None),
            (222, "Hello user 2", None),
            (333, "Hello user 3", None),
        ]

        with patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            result = await send_messages_batch(bot=mock_bot, messages=messages)

        assert result == 2

    @pytest.mark.django_db
    async def test_send_batch_empty_list(self):
        from horoscope.tasks.messaging import send_messages_batch

        mock_bot = MagicMock()

        result = await send_messages_batch(bot=mock_bot, messages=[])

        assert result == 0

    @pytest.mark.django_db
    async def test_send_batch_with_keyboards(self):
        from horoscope.tasks.messaging import send_messages_batch

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()
        mock_keyboard = MagicMock()
        mock_bot = MagicMock()

        messages = [
            (111, "Hello", mock_keyboard),
        ]

        with patch('telegram_bot.app_context.AppContext.for_user', return_value=mock_app_context):
            result = await send_messages_batch(bot=mock_bot, messages=messages)

        assert result == 1
        mock_app_context.send_message.assert_called_once_with(
            text="Hello",
            reply_markup=mock_keyboard,
        )
