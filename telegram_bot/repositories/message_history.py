from datetime import datetime
from typing import Any, Dict, List, Optional

from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.utils import timezone

from core.repositories.base import BaseRepository
from telegram_bot.entities import MessageHistoryEntity
from telegram_bot.exceptions import MessageHistoryNotFoundException
from telegram_bot.models import MessageHistory


class MessageHistoryRepository(BaseRepository[MessageHistory, MessageHistoryEntity]):
    def __init__(self) -> None:
        super().__init__(
            model=MessageHistory,
            entity=MessageHistoryEntity,
            not_found_exception=MessageHistoryNotFoundException,
        )

    def log_message(
        self,
        from_user_telegram_uid: int,
        chat_telegram_uid: int,
        text: Optional[str] = None,
        callback_query: Optional[str] = None,
        to_user_telegram_uid: Optional[int] = None,
        raw: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> MessageHistoryEntity:
        message = MessageHistory.objects.create(
            from_user_telegram_uid=from_user_telegram_uid,
            chat_telegram_uid=chat_telegram_uid,
            text=text,
            callback_query=callback_query,
            to_user_telegram_uid=to_user_telegram_uid,
            raw=raw,
            context=context,
        )
        return MessageHistoryEntity.from_model(message)

    @sync_to_async
    def alog_message(
        self,
        from_user_telegram_uid: int,
        chat_telegram_uid: int,
        text: Optional[str] = None,
        callback_query: Optional[str] = None,
        to_user_telegram_uid: Optional[int] = None,
        raw: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> MessageHistoryEntity:
        close_old_connections()
        return self.log_message(
            from_user_telegram_uid=from_user_telegram_uid,
            chat_telegram_uid=chat_telegram_uid,
            text=text,
            callback_query=callback_query,
            to_user_telegram_uid=to_user_telegram_uid,
            raw=raw,
            context=context,
        )

    def get_by_user(
        self,
        telegram_uid: int,
        limit: Optional[int] = None,
    ) -> List[MessageHistoryEntity]:
        queryset = MessageHistory.objects.filter(
            from_user_telegram_uid=telegram_uid,
        ).order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return MessageHistoryEntity.from_models(list(queryset))

    @sync_to_async
    def aget_by_user(
        self,
        telegram_uid: int,
        limit: Optional[int] = None,
    ) -> List[MessageHistoryEntity]:
        close_old_connections()
        return self.get_by_user(telegram_uid=telegram_uid, limit=limit)

    def count_by_user(
        self,
        telegram_uid: int,
        since: Optional[datetime] = None,
    ) -> int:
        queryset = MessageHistory.objects.filter(
            from_user_telegram_uid=telegram_uid,
        )
        if since:
            queryset = queryset.filter(created_at__gte=since)
        return queryset.count()

    @sync_to_async
    def acount_by_user(
        self,
        telegram_uid: int,
        since: Optional[datetime] = None,
    ) -> int:
        close_old_connections()
        return self.count_by_user(telegram_uid=telegram_uid, since=since)

    def delete_old_messages(self, days: int = 30) -> int:
        from datetime import timedelta
        threshold = timezone.now() - timedelta(days=days)
        count, _ = MessageHistory.objects.filter(created_at__lt=threshold).delete()
        return count

    @sync_to_async
    def adelete_old_messages(self, days: int = 30) -> int:
        close_old_connections()
        return self.delete_old_messages(days=days)
