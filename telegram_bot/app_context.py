import logging
import traceback
from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message, ReactionTypeEmoji
from asgiref.sync import sync_to_async
from dependency_injector.wiring import Provide, inject

from core.containers import ApplicationContainer
from telegram_bot.helpers import fix_unserializable_values_in_raw
from telegram_bot.repositories import MessageHistoryRepository

logger = logging.getLogger(__name__)


class AppContext:
    """
    Message management context with automatic DB logging.

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
            ApplicationContainer.core.message_history_repository
        ],
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

        Use this when sending messages outside the handler flow
        (e.g., background tasks, Celery).
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
        if text is None and reply_markup is None:
            return

        if message_id is None:
            message_id = self._get_message_id(conversation)
        if message_id is None:
            logger.warning(f"No message ID found for conversation '{conversation}'")
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
                logger.warning(f'Message is not modified. {traceback.format_exc()}')
            else:
                raise

    def _init_conversation_data(self, conversation: str) -> None:
        if conversation not in self.conversations:
            self.conversations[conversation] = {
                'message_id': None,
                'messages_to_delete': [],
            }

    def _save_message_id(self, message_id: int, conversation: str) -> None:
        self._init_conversation_data(conversation)
        self.conversations[conversation]['message_id'] = message_id

    def _get_message_id(self, conversation: str) -> Optional[int]:
        if conversation not in self.conversations:
            return None
        return self.conversations[conversation].get('message_id')

    def add_message_to_delete(self, message_id: int, conversation: str = 'main') -> None:
        self._init_conversation_data(conversation)
        if message_id not in self.conversations[conversation]['messages_to_delete']:
            self.conversations[conversation]['messages_to_delete'].append(message_id)

    async def delete_main_message(self) -> None:
        message_id = self._get_message_id('main')
        if message_id is None:
            return

        try:
            await self.bot.delete_message(self.chat_id, message_id)
        except Exception as e:
            logger.debug(f"Failed to delete message {message_id}: {e}", exc_info=e)

        if 'main' in self.conversations:
            self.conversations['main']['message_id'] = None

    async def delete_messages(self, conversation: str = 'main') -> None:
        self._init_conversation_data(conversation)

        for msg_id in self.conversations[conversation]['messages_to_delete']:
            try:
                await self.bot.delete_message(self.chat_id, msg_id)
            except Exception as e:
                logger.debug(f"Failed to delete message {msg_id}: {e}", exc_info=e)

        self.conversations[conversation]['messages_to_delete'] = []

    async def delete_message(self, message_id: int) -> bool:
        try:
            return await self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message_id,
            )
        except Exception as e:
            # Deletion failure must not break the flow — best-effort
            logger.debug(f"Failed to delete message {message_id}: {e}", exc_info=e)
            return False

    async def delete_message_silently(self, message: Optional[Message]) -> None:
        if message is None:
            return

        try:
            await message.delete()
        except Exception as e:
            logger.debug(f"Failed to delete message {message.message_id}", exc_info=e)

    async def send_photo(
        self,
        photo: Any,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        reply_to_message_id: Optional[int] = None,
        parse_mode: Optional[str] = ParseMode.HTML,
        **kwargs: Any,
    ) -> Message:
        message = await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            **kwargs,
        )
        await self._log_message_to_db(message)
        return message

    async def send_video(
        self,
        video: Any,
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        reply_to_message_id: Optional[int] = None,
        parse_mode: Optional[str] = ParseMode.HTML,
        **kwargs: Any,
    ) -> Message:
        message = await self.bot.send_video(
            chat_id=self.chat_id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            supports_streaming=True,
            **kwargs,
        )
        await self._log_message_to_db(message)
        return message

    async def send_dice(
        self,
        emoji: str = "\U0001f3b2",
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        message = await self.bot.send_dice(
            chat_id=self.chat_id,
            emoji=emoji,
            reply_to_message_id=reply_to_message_id,
        )
        await self._log_dice_to_db(message)
        return message

    async def set_reaction(
        self,
        message_id: int,
        emoji: str = "\U0001f389",
        is_big: bool = True,
    ) -> None:
        try:
            await self.bot.set_message_reaction(
                chat_id=self.chat_id,
                message_id=message_id,
                reaction=[ReactionTypeEmoji(emoji=emoji)],
                is_big=is_big,
            )
        except Exception as e:
            logger.debug(f"Failed to set reaction on message {message_id}: {e}", exc_info=e)

    async def _log_message_to_db(self, message: Message) -> None:
        @sync_to_async
        def _db_insert() -> None:
            self.message_history_repo.log_message(
                from_user_telegram_uid=self.bot_id,
                chat_telegram_uid=self.chat_id,
                text=message.text or message.caption,
                to_user_telegram_uid=self.chat_id,
                raw=fix_unserializable_values_in_raw(message.model_dump()),
                callback_query=None,
                context=None,
            )

        await _db_insert()

    async def _log_dice_to_db(self, message: Message) -> None:
        dice_value = message.dice.value if message.dice else None
        dice_emoji = message.dice.emoji if message.dice else "\U0001f3b2"
        text = f"{dice_emoji} Dice: {dice_value}" if dice_value else f"{dice_emoji} Dice"

        @sync_to_async
        def _db_insert() -> None:
            self.message_history_repo.log_message(
                from_user_telegram_uid=self.bot_id,
                chat_telegram_uid=self.chat_id,
                text=text,
                to_user_telegram_uid=self.chat_id,
                raw=fix_unserializable_values_in_raw(message.model_dump()),
                callback_query=None,
                context=None,
            )

        await _db_insert()
