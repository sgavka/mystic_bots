"""
Pydantic entities for telegram_bot app.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from core.base_entity import BaseEntity


class MessageHistoryEntity(BaseEntity):
    """Entity for MessageHistory model."""

    id: int
    from_user_telegram_uid: Optional[int] = None
    to_user_telegram_uid: Optional[int] = None
    chat_telegram_uid: Optional[int] = None
    text: Optional[str] = None
    callback_query: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
