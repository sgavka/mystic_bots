from datetime import date
from typing import Optional

from asgiref.sync import sync_to_async

from core.repositories.base import BaseRepository
from horoscope.entities import HoroscopeEntity
from horoscope.exceptions import HoroscopeNotFoundException
from horoscope.models import Horoscope


class HoroscopeRepository(BaseRepository[Horoscope, HoroscopeEntity]):
    def __init__(self):
        super().__init__(
            model=Horoscope,
            entity=HoroscopeEntity,
            not_found_exception=HoroscopeNotFoundException,
        )

    def get_by_user_and_date(
        self,
        telegram_uid: int,
        target_date: date,
    ) -> Optional[HoroscopeEntity]:
        try:
            horoscope = Horoscope.objects.get(
                user_telegram_uid=telegram_uid,
                date=target_date,
            )
            return HoroscopeEntity.from_model(horoscope)
        except Horoscope.DoesNotExist:
            return None

    async def aget_by_user_and_date(
        self,
        telegram_uid: int,
        target_date: date,
    ) -> Optional[HoroscopeEntity]:
        return await sync_to_async(self.get_by_user_and_date)(telegram_uid, target_date)

    def create_horoscope(
        self,
        telegram_uid: int,
        horoscope_type: str,
        target_date: date,
        full_text: str,
        teaser_text: str,
    ) -> HoroscopeEntity:
        horoscope = Horoscope.objects.create(
            user_telegram_uid=telegram_uid,
            horoscope_type=horoscope_type,
            date=target_date,
            full_text=full_text,
            teaser_text=teaser_text,
        )
        return HoroscopeEntity.from_model(horoscope)

    async def acreate_horoscope(
        self,
        telegram_uid: int,
        horoscope_type: str,
        target_date: date,
        full_text: str,
        teaser_text: str,
    ) -> HoroscopeEntity:
        return await sync_to_async(self.create_horoscope)(
            telegram_uid,
            horoscope_type,
            target_date,
            full_text,
            teaser_text,
        )
