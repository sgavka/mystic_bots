"""Tests for telegram_bot.app_context module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message

from telegram_bot.app_context import AppContext


def _create_app_context(
    chat_id: int = 12345,
    bot_id: int = 99999,
) -> AppContext:
    """Create AppContext with mocked dependencies."""
    bot = AsyncMock()
    bot.id = bot_id
    message_history_repo = MagicMock()

    ctx = AppContext.__new__(AppContext)
    ctx.bot = bot
    ctx.chat_id = chat_id
    ctx.bot_id = bot_id
    ctx.message_history_repo = message_history_repo
    ctx.conversations = {}
    return ctx


def _make_message(
    message_id: int = 1,
    text: str = "Hello",
    caption: str | None = None,
) -> MagicMock:
    """Create a mock Message object that passes isinstance(msg, Message)."""
    msg = MagicMock(spec=Message)
    msg.message_id = message_id
    msg.text = text
    msg.caption = caption
    msg.model_dump.return_value = {"message_id": message_id, "text": text}
    return msg


class TestAppContextInit:

    def test_for_user_factory(self):
        bot = AsyncMock()
        bot.id = 99999

        with patch.object(AppContext, '__init__', return_value=None) as mock_init:
            mock_init.__wrapped__ = lambda *a, **kw: None
            ctx = AppContext.__new__(AppContext)
            ctx.bot = bot
            ctx.chat_id = 55555
            ctx.bot_id = 99999
            ctx.message_history_repo = MagicMock()
            ctx.conversations = {}

        assert ctx.chat_id == 55555
        assert ctx.bot_id == 99999


class TestConversationTracking:

    def test_save_and_get_message_id(self):
        ctx = _create_app_context()

        ctx._save_message_id(message_id=42, conversation='main')
        assert ctx._get_message_id('main') == 42

    def test_get_message_id_nonexistent_conversation(self):
        ctx = _create_app_context()
        assert ctx._get_message_id('nonexistent') is None

    def test_multiple_conversations(self):
        ctx = _create_app_context()

        ctx._save_message_id(message_id=1, conversation='main')
        ctx._save_message_id(message_id=2, conversation='secondary')

        assert ctx._get_message_id('main') == 1
        assert ctx._get_message_id('secondary') == 2

    def test_overwrite_message_id(self):
        ctx = _create_app_context()

        ctx._save_message_id(message_id=1, conversation='main')
        ctx._save_message_id(message_id=2, conversation='main')

        assert ctx._get_message_id('main') == 2

    def test_add_message_to_delete(self):
        ctx = _create_app_context()

        ctx.add_message_to_delete(message_id=10, conversation='main')
        ctx.add_message_to_delete(message_id=20, conversation='main')

        assert ctx.conversations['main']['messages_to_delete'] == [10, 20]

    def test_add_message_to_delete_no_duplicates(self):
        ctx = _create_app_context()

        ctx.add_message_to_delete(message_id=10, conversation='main')
        ctx.add_message_to_delete(message_id=10, conversation='main')

        assert ctx.conversations['main']['messages_to_delete'] == [10]


class TestSendMessage:

    @pytest.mark.asyncio
    async def test_send_message_calls_bot(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=5)
        ctx.bot.send_message.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock):
            result = await ctx.send_message(text="Hello")

        ctx.bot.send_message.assert_called_once()
        assert result == mock_msg

    @pytest.mark.asyncio
    async def test_send_message_logs_to_db(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=5)
        ctx.bot.send_message.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock) as mock_log:
            await ctx.send_message(text="Hello")

        mock_log.assert_called_once_with(mock_msg)

    @pytest.mark.asyncio
    async def test_send_message_saves_conversation_id(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=7)
        ctx.bot.send_message.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock):
            await ctx.send_message(text="Hello", conversation='wizard')

        assert ctx._get_message_id('wizard') == 7


class TestEditMessage:

    @pytest.mark.asyncio
    async def test_edit_message_with_text(self):
        ctx = _create_app_context()
        ctx._save_message_id(message_id=10, conversation='main')
        mock_msg = _make_message(message_id=10)
        ctx.bot.edit_message_text.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock) as mock_log:
            await ctx.edit_message(text="Updated")

        ctx.bot.edit_message_text.assert_called_once()
        mock_log.assert_called_once_with(mock_msg)

    @pytest.mark.asyncio
    async def test_edit_message_with_explicit_message_id(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=15)
        ctx.bot.edit_message_text.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock):
            await ctx.edit_message(text="Updated", message_id=15)

        ctx.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_message_no_text_no_markup_returns_early(self):
        ctx = _create_app_context()
        await ctx.edit_message()
        ctx.bot.edit_message_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_message_no_message_id_warns(self):
        ctx = _create_app_context()
        await ctx.edit_message(text="Updated", conversation='nonexistent')
        ctx.bot.edit_message_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_message_reply_markup_only(self):
        ctx = _create_app_context()
        ctx._save_message_id(message_id=10, conversation='main')
        mock_msg = _make_message(message_id=10)
        markup = MagicMock()
        ctx.bot.edit_message_reply_markup.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock):
            await ctx.edit_message(reply_markup=markup)

        ctx.bot.edit_message_reply_markup.assert_called_once()


class TestDeleteMessage:

    @pytest.mark.asyncio
    async def test_delete_message_success(self):
        ctx = _create_app_context()
        ctx.bot.delete_message.return_value = True
        result = await ctx.delete_message(message_id=10)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_message_failure_returns_false(self):
        ctx = _create_app_context()
        ctx.bot.delete_message.side_effect = Exception("Not found")
        result = await ctx.delete_message(message_id=10)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_main_message(self):
        ctx = _create_app_context()
        ctx._save_message_id(message_id=10, conversation='main')

        await ctx.delete_main_message()

        ctx.bot.delete_message.assert_called_once_with(12345, 10)
        assert ctx._get_message_id('main') is None

    @pytest.mark.asyncio
    async def test_delete_messages_clears_queue(self):
        ctx = _create_app_context()
        ctx.add_message_to_delete(message_id=1)
        ctx.add_message_to_delete(message_id=2)

        await ctx.delete_messages()

        assert ctx.bot.delete_message.call_count == 2
        assert ctx.conversations['main']['messages_to_delete'] == []

    @pytest.mark.asyncio
    async def test_delete_message_silently_with_none(self):
        ctx = _create_app_context()
        await ctx.delete_message_silently(None)
        ctx.bot.delete_message.assert_not_called()


class TestSendPhoto:

    @pytest.mark.asyncio
    async def test_send_photo_logs_to_db(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=20, text=None, caption="Photo caption")
        ctx.bot.send_photo.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock) as mock_log:
            result = await ctx.send_photo(photo="file_id", caption="Photo caption")

        assert result == mock_msg
        mock_log.assert_called_once_with(mock_msg)


class TestSendVideo:

    @pytest.mark.asyncio
    async def test_send_video_logs_to_db(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=30)
        ctx.bot.send_video.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock) as mock_log:
            result = await ctx.send_video(video="file_id")

        assert result == mock_msg
        mock_log.assert_called_once_with(mock_msg)


class TestForUserFactory:

    def test_for_user_creates_context_with_chat_id(self):
        bot = AsyncMock()
        bot.id = 99999

        ctx = AppContext.__new__(AppContext)
        ctx.bot = bot
        ctx.chat_id = 55555
        ctx.bot_id = 99999
        ctx.message_history_repo = MagicMock()
        ctx.conversations = {}

        with patch.object(AppContext, '__init__', return_value=None) as mock_init:
            AppContext.for_user(
                bot=bot,
                user_telegram_uid=55555,
            )

        mock_init.assert_called_once_with(
            bot=bot,
            chat_id=55555,
        )


class TestSendInvoice:

    @pytest.mark.asyncio
    async def test_send_invoice_logs_message(self):
        ctx = _create_app_context()
        mock_msg = _make_message(message_id=40)
        ctx.bot.send_invoice.return_value = mock_msg

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock) as mock_log:
            result = await ctx.send_invoice(
                title="Subscription",
                description="Monthly plan",
                payload="sub_monthly",
                currency="XTR",
                prices=[MagicMock()],
            )

        assert result == mock_msg
        mock_log.assert_called_once_with(mock_msg)

    @pytest.mark.asyncio
    async def test_send_invoice_non_message_result(self):
        ctx = _create_app_context()
        ctx.bot.send_invoice.return_value = True  # Not a Message instance

        with patch.object(ctx, '_log_message_to_db', new_callable=AsyncMock) as mock_log:
            result = await ctx.send_invoice(
                title="Subscription",
                description="Monthly plan",
                payload="sub_monthly",
                currency="XTR",
                prices=[MagicMock()],
            )

        assert result is True
        mock_log.assert_not_called()


class TestSendDice:

    @pytest.mark.asyncio
    async def test_send_dice_logs_to_db(self):
        ctx = _create_app_context()
        mock_msg = MagicMock(spec=Message)
        mock_msg.message_id = 50
        mock_msg.dice = MagicMock()
        mock_msg.dice.value = 4
        mock_msg.dice.emoji = "\U0001f3b2"
        mock_msg.model_dump.return_value = {"message_id": 50}
        ctx.bot.send_dice.return_value = mock_msg

        with patch.object(ctx, '_log_dice_to_db', new_callable=AsyncMock) as mock_log:
            result = await ctx.send_dice()

        assert result == mock_msg
        mock_log.assert_called_once_with(mock_msg)

    @pytest.mark.asyncio
    async def test_send_dice_custom_emoji(self):
        ctx = _create_app_context()
        mock_msg = MagicMock(spec=Message)
        mock_msg.message_id = 51
        mock_msg.dice = MagicMock()
        mock_msg.dice.value = 5
        mock_msg.dice.emoji = "\U0001f3af"
        mock_msg.model_dump.return_value = {"message_id": 51}
        ctx.bot.send_dice.return_value = mock_msg

        with patch.object(ctx, '_log_dice_to_db', new_callable=AsyncMock):
            await ctx.send_dice(emoji="\U0001f3af")

        ctx.bot.send_dice.assert_called_once_with(
            chat_id=12345,
            emoji="\U0001f3af",
            reply_to_message_id=None,
        )


class TestSetReaction:

    @pytest.mark.asyncio
    async def test_set_reaction_success(self):
        ctx = _create_app_context()
        ctx.bot.set_message_reaction.return_value = True

        await ctx.set_reaction(message_id=10)

        ctx.bot.set_message_reaction.assert_called_once()
        call_kwargs = ctx.bot.set_message_reaction.call_args[1]
        assert call_kwargs['chat_id'] == 12345
        assert call_kwargs['message_id'] == 10
        assert call_kwargs['is_big'] is True

    @pytest.mark.asyncio
    async def test_set_reaction_failure_does_not_raise(self):
        ctx = _create_app_context()
        ctx.bot.set_message_reaction.side_effect = Exception("API error")

        # Should not raise
        await ctx.set_reaction(message_id=10)

    @pytest.mark.asyncio
    async def test_set_reaction_custom_emoji(self):
        ctx = _create_app_context()
        ctx.bot.set_message_reaction.return_value = True

        await ctx.set_reaction(message_id=10, emoji="\U0001f44d", is_big=False)

        call_kwargs = ctx.bot.set_message_reaction.call_args[1]
        assert call_kwargs['is_big'] is False
