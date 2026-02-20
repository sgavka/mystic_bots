from datetime import date, datetime
from typing import Optional

from asgiref.sync import sync_to_async
from django.utils import timezone

from core.repositories.base import BaseRepository
from horoscope.entities import HoroscopeEntity
from horoscope.enums import HoroscopeType
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
        horoscope_type: HoroscopeType,
        target_date: date,
        full_text: str,
        teaser_text: str,
        extended_teaser_text: str = '',
    ) -> HoroscopeEntity:
        horoscope = Horoscope.objects.create(
            user_telegram_uid=telegram_uid,
            horoscope_type=horoscope_type,
            date=target_date,
            full_text=full_text,
            teaser_text=teaser_text,
            extended_teaser_text=extended_teaser_text,
        )
        return HoroscopeEntity.from_model(horoscope)

    async def acreate_horoscope(
        self,
        telegram_uid: int,
        horoscope_type: HoroscopeType,
        target_date: date,
        full_text: str,
        teaser_text: str,
        extended_teaser_text: str = '',
    ) -> HoroscopeEntity:
        return await sync_to_async(self.create_horoscope)(
            telegram_uid,
            horoscope_type,
            target_date,
            full_text,
            teaser_text,
            extended_teaser_text,
        )

    def mark_sent(self, horoscope_id: int) -> None:
        Horoscope.objects.filter(id=horoscope_id).update(sent_at=timezone.now())

    async def amark_sent(self, horoscope_id: int) -> None:
        return await sync_to_async(self.mark_sent)(horoscope_id)

    def mark_failed_to_send(self, horoscope_id: int) -> None:
        Horoscope.objects.filter(id=horoscope_id).update(failed_to_send_at=timezone.now())

    async def amark_failed_to_send(self, horoscope_id: int) -> None:
        return await sync_to_async(self.mark_failed_to_send)(horoscope_id)

    def get_last_sent_at(self, telegram_uid: int) -> Optional[datetime]:
        horoscope = (
            Horoscope.objects
            .filter(user_telegram_uid=telegram_uid, sent_at__isnull=False)
            .order_by('-sent_at')
            .values_list('sent_at', flat=True)
            .first()
        )
        return horoscope

    async def aget_last_sent_at(self, telegram_uid: int) -> Optional[datetime]:
        return await sync_to_async(self.get_last_sent_at)(telegram_uid)

    def count_created_since(self, since: date) -> int:
        return Horoscope.objects.filter(created_at__date__gte=since).count()

    async def acount_created_since(self, since: date) -> int:
        return await sync_to_async(self.count_created_since)(since)
