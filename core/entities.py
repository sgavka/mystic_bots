from datetime import datetime
from typing import Any, Optional

from core.base_entity import BaseEntity


class SettingEntity(BaseEntity):
    name: str
    value: Any
    type: str
    created_at: datetime
    updated_at: datetime

    def get_typed_value(self) -> Any:
        if self.type == 'string':
            return str(self.value)
        elif self.type == 'integer':
            return int(self.value)
        elif self.type == 'boolean':
            return bool(self.value)
        elif self.type == 'json':
            return self.value
        return self.value


class UserEntity(BaseEntity):
    telegram_uid: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p) or self.username or str(self.telegram_uid)
