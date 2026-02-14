import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update
from asgiref.sync import sync_to_async
from django.utils import timezone

from core.containers import container
from core.entities import UserEntity
from telegram_bot.helpers import fix_unserializable_values_in_raw

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.user_repository = container.core.user_repository()

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

        if user_obj is None:
            return await handler(event, data)

        user = await self._update_or_create_user(
            telegram_uid=user_obj.id,
            first_name=user_obj.first_name,
            last_name=user_obj.last_name,
            username=user_obj.username,
            language_code=user_obj.language_code,
            is_premium=user_obj.is_premium or False,
        )

        data['user'] = user

        return await handler(event, data)

    async def _update_or_create_user(
        self,
        telegram_uid: int,
        first_name: Optional[str],
        last_name: Optional[str],
        username: Optional[str],
        language_code: Optional[str],
        is_premium: bool,
    ) -> UserEntity:
        from django.db import close_old_connections

        @sync_to_async
        def _db_update_or_create() -> UserEntity:
            close_old_connections()
            user, _created = self.user_repository.update_or_create(
                telegram_uid=telegram_uid,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'language_code': language_code,
                    'is_premium': is_premium,
                    'last_activity': timezone.now(),
                },
            )
            return user

        return await _db_update_or_create()


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, bot_id: int) -> None:
        super().__init__()
        self.bot_id = bot_id
        self.message_history_repository = container.core.message_history_repository()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        await self._log_message(event=event, data=data)
        return await handler(event, data)

    async def _log_message(
        self,
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> None:
        message = None
        callback_query = None

        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            callback_query = event
            message = event.message
        elif isinstance(event, Update):
            if event.message:
                message = event.message
            elif event.callback_query:
                callback_query = event.callback_query
                message = event.callback_query.message

        if not message:
            return

        from_user_id = message.from_user.id if message.from_user else None
        chat_id = message.chat.id
        to_user_id = self.bot_id

        text = None
        callback_data = None

        if callback_query:
            callback_data = callback_query.data
        elif message.dice:
            dice_emoji = message.dice.emoji
            dice_value = message.dice.value
            text = f"{dice_emoji} Dice: {dice_value}"
        else:
            text = message.text or message.caption

        @sync_to_async
        def _db_insert() -> None:
            from django.db import close_old_connections

            close_old_connections()
            self.message_history_repository.log_message(
                from_user_telegram_uid=from_user_id,
                to_user_telegram_uid=to_user_id,
                chat_telegram_uid=chat_id,
                text=text,
                callback_query=callback_data,
                raw=fix_unserializable_values_in_raw(message.model_dump()),
                context=None,
            )

        await _db_insert()


class AppContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from telegram_bot.app_context import AppContext

        bot = data.get('bot')
        chat_id = None

        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id if event.message else event.from_user.id

        if bot and chat_id:
            app_context = AppContext(bot=bot, chat_id=chat_id)
            data['app_context'] = app_context

        return await handler(event, data)
