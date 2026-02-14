from datetime import datetime
from typing import Any, Dict, Optional

from core.base_entity import BaseEntity


class MessageHistoryEntity(BaseEntity):
    id: int
    from_user_telegram_uid: int
    to_user_telegram_uid: Optional[int] = None
    chat_telegram_uid: int
    text: Optional[str] = None
    callback_query: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
