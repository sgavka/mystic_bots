"""
MessageHistory repository for logging messages.
"""
from typing import Optional, Any, Dict

from asgiref.sync import sync_to_async
from django.db import close_old_connections

from core.repositories.base import BaseRepository
from telegram_bot.entities import MessageHistoryEntity
from telegram_bot.exceptions import MessageHistoryNotFoundException
from telegram_bot.models import MessageHistory


class MessageHistoryRepository(BaseRepository[MessageHistory, MessageHistoryEntity]):
    """
    Repository for MessageHistory model operations.
    """

    def __init__(self) -> None:
        """Initialize MessageHistoryRepository."""
        super().__init__(
            model=MessageHistory,
            entity=MessageHistoryEntity,
            not_found_exception=MessageHistoryNotFoundException,
        )

    def log_message(
        self,
        from_user_telegram_uid: Optional[int] = None,
        to_user_telegram_uid: Optional[int] = None,
        chat_telegram_uid: Optional[int] = None,
        text: Optional[str] = None,
        callback_query: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> MessageHistoryEntity:
        """
        Log a message to the database.

        Args:
            from_user_telegram_uid: Sender's Telegram UID
            to_user_telegram_uid: Recipient's Telegram UID
            chat_telegram_uid: Chat Telegram UID
            text: Message text
            callback_query: Callback query data
            raw: Raw message data
            context: Additional context data

        Returns:
            Created MessageHistoryEntity
        """
        message = MessageHistory.objects.create(
            from_user_telegram_uid=from_user_telegram_uid,
            to_user_telegram_uid=to_user_telegram_uid,
            chat_telegram_uid=chat_telegram_uid,
            text=text,
            callback_query=callback_query,
            raw=raw,
            context=context,
        )
        return MessageHistoryEntity.from_model(message)

    async def alog_message(
        self,
        from_user_telegram_uid: Optional[int] = None,
        to_user_telegram_uid: Optional[int] = None,
        chat_telegram_uid: Optional[int] = None,
        text: Optional[str] = None,
        callback_query: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> MessageHistoryEntity:
        """Async version: Log a message to the database."""
        close_old_connections()
        return await sync_to_async(self.log_message)(
            from_user_telegram_uid=from_user_telegram_uid,
            to_user_telegram_uid=to_user_telegram_uid,
            chat_telegram_uid=chat_telegram_uid,
            text=text,
            callback_query=callback_query,
            raw=raw,
            context=context,
        )
