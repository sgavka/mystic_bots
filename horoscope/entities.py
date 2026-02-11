from datetime import date, datetime
from typing import Optional

from core.base_entity import BaseEntity


class UserProfileEntity(BaseEntity):
    user_telegram_uid: int
    name: str
    date_of_birth: date
    place_of_birth: str
    place_of_living: str
    preferred_language: str = 'en'
    created_at: datetime
    updated_at: datetime


class HoroscopeEntity(BaseEntity):
    id: int
    user_telegram_uid: int
    horoscope_type: str
    date: date
    full_text: str
    teaser_text: str
    created_at: datetime


class SubscriptionEntity(BaseEntity):
    id: int
    user_telegram_uid: int
    status: str
    started_at: datetime
    expires_at: Optional[datetime] = None
    telegram_payment_charge_id: Optional[str] = None
    reminder_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        return self.status == 'active'
