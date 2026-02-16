from datetime import date, datetime, time
from typing import Optional

from core.base_entity import BaseEntity


class UserProfileEntity(BaseEntity):
    user_telegram_uid: int
    name: str
    date_of_birth: date
    place_of_birth: str
    place_of_living: str
    birth_time: Optional[time] = None
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
    extended_teaser_text: str = ''
    sent_at: Optional[datetime] = None
    failed_to_send_at: Optional[datetime] = None
    created_at: datetime


class LLMUsageEntity(BaseEntity):
    id: int
    horoscope_id: int
    model: str
    input_tokens: int
    output_tokens: int
    created_at: datetime


class HoroscopeFollowupEntity(BaseEntity):
    id: int
    horoscope_id: int
    question_text: str
    answer_text: str
    model: str
    input_tokens: int
    output_tokens: int
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
