from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update
from asgiref.sync import sync_to_async
from django.utils import timezone

from core.containers import container
from core.entities import UserEntity


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.user_repository = container.core.user_repository()
        self.message_history_repository = container.core.message_history_repository()

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

        await self._log_message(event=event, user_uid=user_obj.id)

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
                    'last_activity': timezone.now(),
                },
            )
            return user

        return await _db_update_or_create()


    async def _log_message(self, event: TelegramObject, user_uid: int) -> None:
        import logging

        logger = logging.getLogger(__name__)

        try:
            text = None
            callback_query = None
            chat_id = user_uid

            if isinstance(event, Message):
                text = event.text
                chat_id = event.chat.id
            elif isinstance(event, CallbackQuery):
                callback_query = event.data
                if event.message:
                    chat_id = event.message.chat.id

            await self.message_history_repository.alog_message(
                from_user_telegram_uid=user_uid,
                chat_telegram_uid=chat_id,
                text=text,
                callback_query=callback_query,
            )
        except Exception:
            logger.exception("Failed to log message history")


class AppContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from telegram_bot.utils.context import AppContext

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
