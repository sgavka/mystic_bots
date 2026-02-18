"""
User middleware for aiogram bot
"""
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineQuery, Message, TelegramObject, Update
from asgiref.sync import sync_to_async
from dependency_injector.wiring import Provide, inject

from core.containers import ApplicationContainer
from core.entities import UserEntity
from core.repositories import UserRepository
from telegram_bot.helpers import fix_unserializable_values_in_raw
from telegram_bot.repositories import MessageHistoryRepository


class UserMiddleware(BaseMiddleware):
    """
    Middleware to initialize user records.
    """

    @inject
    def __init__(
            self,
            user_repository: UserRepository = Provide[ApplicationContainer.core.user_repository],
    ):
        super().__init__()
        self.user_repository = user_repository

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Extract user from event
        user_obj = None
        if isinstance(event, Message):
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery):
            user_obj = event.from_user
        elif isinstance(event, InlineQuery):
            user_obj = event.from_user
        elif isinstance(event, Update):
            if event.message:
                user_obj = event.message.from_user
            elif event.callback_query:
                user_obj = event.callback_query.from_user
            elif event.inline_query:
                user_obj = event.inline_query.from_user

        if user_obj is None:
            return await handler(event, data)

        # Update or create shared User record
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
        """Update or create shared User record (async-safe)."""
        from django.db import close_old_connections

        @sync_to_async
        def _db_update_or_create():
            close_old_connections()
            user, created = self.user_repository.update_or_create(
                telegram_uid=telegram_uid,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'language_code': language_code,
                    'is_premium': is_premium,
                }
            )
            return user

        return await _db_update_or_create()


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging user messages
    """

    @inject
    def __init__(
            self,
            bot_id: int,
            message_history_repository: MessageHistoryRepository = Provide[
                ApplicationContainer.telegram_bot.message_history_repository
            ]
    ):
        super().__init__()
        self.bot_id = bot_id
        self.message_history_repository = message_history_repository

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        await self._log_message(event, data)
        return await handler(event, data)

    async def _log_message(
            self,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> None:
        """Log incoming message to database"""
        from asgiref.sync import sync_to_async

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

        if message and message.chat.type == 'channel':
            return

        if not message:
            return

        from_user_id = message.from_user.id if message.from_user else None
        chat_id = message.chat.id
        to_user_id = None
        group_id = None

        if message.chat.type in ['group', 'supergroup']:
            group_id = message.chat.id
            if message.reply_to_message and message.reply_to_message.from_user:
                to_user_id = message.reply_to_message.from_user.id
        else:
            to_user_id = self.bot_id

        text = None
        callback_data = None

        if callback_query:
            callback_data = callback_query.data
        elif message.dice:
            # Log dice messages with dice value
            dice_emoji = message.dice.emoji
            dice_value = message.dice.value
            text = f"{dice_emoji} Dice: {dice_value}"
        else:
            text = message.text or message.caption

        context_data = data.get('state_data', {})

        @sync_to_async
        def _db_insert():
            from django.db import close_old_connections
            close_old_connections()
            self.message_history_repository.log_message(
                from_user_telegram_uid=from_user_id,
                to_user_telegram_uid=to_user_id,
                chat_telegram_uid=group_id if group_id else chat_id,
                text=text,
                callback_query=callback_data,
                raw=fix_unserializable_values_in_raw(message.model_dump()),
                context=context_data if context_data else None,
            )

        await _db_insert()


class AppContextMiddleware(BaseMiddleware):
    """
    Middleware to attach AppContext to handler data
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        from telegram_bot.app_context import AppContext

        bot = data.get('bot')
        chat_id = None

        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id if event.message else event.from_user.id

        if bot and chat_id:
            app_context = AppContext(
                bot=bot,
                chat_id=chat_id,
            )
            data['app_context'] = app_context

        return await handler(event, data)
