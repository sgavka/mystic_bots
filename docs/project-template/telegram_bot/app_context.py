"""
AppContext class for aiogram bot

Provides message management with conversation tracking, message editing,
deletion queues, and database logging via repository pattern with DI.
"""
from typing import Optional, Dict, Any

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup, ReactionTypeEmoji
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
import logging
import traceback

from dependency_injector.wiring import inject, Provide

from core.containers import ApplicationContainer
from telegram_bot.helpers import fix_unserializable_values_in_raw
from telegram_bot.repositories import MessageHistoryRepository


class AppContext:
    """
    Async version of CustomContext for message management.

    Provides:
    - Message sending with automatic logging to MessageHistory
    - Conversation tracking (save/get message_id per conversation)
    - Message deletion queues
    """

    @inject
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        bot_id: Optional[int] = None,
        message_history_repo: MessageHistoryRepository = Provide[
            ApplicationContainer.telegram_bot.message_history_repository
        ],
        # TODO: Add project-specific dependencies here if needed
        # (e.g., user_to_bot_repo for bot-blocked tracking)
    ):
        self.bot = bot
        self.chat_id = chat_id
        self.bot_id = bot_id or bot.id
        self.message_history_repo = message_history_repo

        self.conversations: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def for_user(
        cls,
        bot: Bot,
        user_telegram_uid: int,
    ) -> 'AppContext':
        """
        Factory method to create AppContext for a specific user.

        Use this when you need to send messages to a user outside the normal
        handler flow (e.g., background tasks, opponent notifications).

        Args:
            bot: Bot instance
            user_telegram_uid: User's Telegram UID to send messages to

        Returns:
            AppContext configured for the specified user
        """
        return cls(
            bot=bot,
            chat_id=user_telegram_uid,
        )

    async def send_message(
        self,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        conversation: str = 'main',
        reply_to_message_id: Optional[int] = None,
        parse_mode: Optional[str] = ParseMode.HTML,
        disable_web_page_preview: bool = True,
    ) -> Message:
        """
        Send a message and track it in conversation
        """
        # TODO: Add TelegramForbiddenError handling here if needed
        # (e.g., mark bot as blocked when user blocks the bot)
        message = await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            reply_to_message_id=reply_to_message_id,
        )

        await self._log_message_to_db(message)
        self._save_message_id(message.message_id, conversation)

        return message

    async def edit_message(
        self,
        text: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        conversation: str = 'main',
        parse_mode: Optional[str] = ParseMode.HTML,
        disable_web_page_preview: bool = True,
        message_id: Optional[int] = None,
    ) -> None:
        """
        Edit the last message in conversation
        """
        if text is None and reply_markup is None:
            return

        if message_id is None:
            message_id = self._get_message_id(conversation)
        if message_id is None:
            logging.warning(f"No message ID found for conversation '{conversation}'")
            return

        try:
            message = None

            if text is not None and reply_markup is None:
                message = await self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=message_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                )
            elif text is None and reply_markup is not None:
                message = await self.bot.edit_message_reply_markup(
                    chat_id=self.chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup,
                )
            elif text is not None and reply_markup is not None:
                message = await self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                )

            if message is not None:
                await self._log_message_to_db(message)

        except TelegramBadRequest as e:
            if 'message is not modified' in str(e).lower():
                logging.warning(f'Message is not modified. {traceback.format_exc()}')
            else:
                raise e

    def _init_conversation_data(self, conversation: str) -> None:
        """Initialize conversation data structure if not exists"""
        if conversation not in self.conversations:
            self.conversations[conversation] = {
                'message_id': None,
                'messages_to_delete': []
            }

    def _save_message_id(self, message_id: int, conversation: str) -> None:
        """Save message ID for conversation"""
        self._init_conversation_data(conversation)
        self.conversations[conversation]['message_id'] = message_id

    def _get_message_id(self, conversation: str) -> Optional[int]:
        """Get message ID for conversation"""
        if conversation not in self.conversations:
            return None
        return self.conversations[conversation].get('message_id')

    def add_message_to_delete(self, message_id: int, conversation: str = 'main') -> None:
        """Add message to deletion queue"""
        self._init_conversation_data(conversation)
        if message_id not in self.conversations[conversation]['messages_to_delete']:
            self.conversations[conversation]['messages_to_delete'].append(message_id)

    async def delete_main_message(self) -> None:
        """Delete the main conversation message"""
        message_id = self._get_message_id('main')
        if message_id is None:
            return

        try:
            await self.bot.delete_message(self.chat_id, message_id)
        except Exception as e:
            logging.debug(f"Failed to delete message {message_id}: {e}", exc_info=e)

        if 'main' in self.conversations:
            self.conversations['main']['message_id'] = None

    async def delete_messages(self, conversation: str = 'main') -> None:
        """Delete all messages in deletion queue for conversation"""
        self._init_conversation_data(conversation)

        for message_id in self.conversations[conversation]['messages_to_delete']:
            try:
                await self.bot.delete_message(self.chat_id, message_id)
            except Exception as e:
                logging.debug(f"Failed to delete message {message_id}: {e}", exc_info=e)

        self.conversations[conversation]['messages_to_delete'] = []

    async def delete_message_silently(self, message: Optional[Message]) -> None:
        """Silently delete a message without raising exceptions"""
        if message is None:
            return

        try:
            await message.delete()
        except Exception as e:
            logging.debug(f"Failed to delete message {message.message_id}", exc_info=e)

    async def send_video(
        self,
        video: Any,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        reply_to_message_id: Optional[int] = None,
        parse_mode: Optional[str] = ParseMode.HTML,
        **kwargs,
    ) -> Message:
        """Send a video and log it to database."""
        message = await self.bot.send_video(
            chat_id=self.chat_id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            supports_streaming=True,
            **kwargs
        )
        await self._log_message_to_db(message)
        return message

    async def send_photo(
        self,
        photo: Any,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        reply_to_message_id: Optional[int] = None,
        parse_mode: Optional[str] = ParseMode.HTML,
        **kwargs,
    ) -> Message:
        """Send a photo and log it to database"""
        message = await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )
        await self._log_message_to_db(message)
        return message

    async def send_dice(
        self,
        emoji: str = "🎲",
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a dice animation and log it to database"""
        message = await self.bot.send_dice(
            chat_id=self.chat_id,
            emoji=emoji,
            reply_to_message_id=reply_to_message_id,
        )
        await self._log_dice_to_db(message)
        return message

    async def _log_message_to_db(self, message: Message) -> None:
        """Log message to database using repository pattern"""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _db_insert():
            self.message_history_repo.log_message(
                from_user_telegram_uid=self.bot_id,
                chat_telegram_uid=self.chat_id,
                text=message.text or message.caption,
                to_user_telegram_uid=self.chat_id,
                raw=fix_unserializable_values_in_raw(message.model_dump()),
                callback_query=None,
                context=None
            )

        await _db_insert()

    async def _log_dice_to_db(self, message: Message) -> None:
        """Log dice message to database using repository pattern"""
        from asgiref.sync import sync_to_async

        dice_value = message.dice.value if message.dice else None
        dice_emoji = message.dice.emoji if message.dice else "🎲"
        text = f"{dice_emoji} Dice: {dice_value}" if dice_value else f"{dice_emoji} Dice"

        @sync_to_async
        def _db_insert():
            self.message_history_repo.log_message(
                from_user_telegram_uid=self.bot_id,
                chat_telegram_uid=self.chat_id,
                text=text,
                to_user_telegram_uid=self.chat_id,
                raw=fix_unserializable_values_in_raw(message.model_dump()),
                callback_query=None,
                context=None
            )

        await _db_insert()

    async def set_reaction(
        self,
        message_id: int,
        emoji: str = "🎉",
        is_big: bool = True,
    ) -> None:
        """
        Set a reaction on a message.

        Args:
            message_id: Message ID to react to
            emoji: Emoji to use as reaction
            is_big: Whether to use a big reaction animation
        """
        try:
            await self.bot.set_message_reaction(
                chat_id=self.chat_id,
                message_id=message_id,
                reaction=[ReactionTypeEmoji(emoji=emoji)],
                is_big=is_big,
            )
        except Exception as e:
            logging.debug(f"Failed to set reaction on message {message_id}: {e}", exc_info=e)
