from typing import List

from asgiref.sync import sync_to_async

from core.repositories.base import BaseRepository
from horoscope.entities import HoroscopeFollowupEntity
from horoscope.exceptions import HoroscopeFollowupNotFoundException
from horoscope.models import HoroscopeFollowup


class HoroscopeFollowupRepository(BaseRepository[HoroscopeFollowup, HoroscopeFollowupEntity]):
    def __init__(self):
        super().__init__(
            model=HoroscopeFollowup,
            entity=HoroscopeFollowupEntity,
            not_found_exception=HoroscopeFollowupNotFoundException,
        )

    def create_followup(
        self,
        horoscope_id: int,
        question_text: str,
        answer_text: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> HoroscopeFollowupEntity:
        followup = HoroscopeFollowup.objects.create(
            horoscope_id=horoscope_id,
            question_text=question_text,
            answer_text=answer_text,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        return HoroscopeFollowupEntity.from_model(followup)

    async def acreate_followup(
        self,
        horoscope_id: int,
        question_text: str,
        answer_text: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> HoroscopeFollowupEntity:
        return await sync_to_async(self.create_followup)(
            horoscope_id,
            question_text,
            answer_text,
            model,
            input_tokens,
            output_tokens,
        )

    def get_by_horoscope(self, horoscope_id: int) -> List[HoroscopeFollowupEntity]:
        followups = HoroscopeFollowup.objects.filter(
            horoscope_id=horoscope_id,
        ).order_by('created_at')
        return HoroscopeFollowupEntity.from_models(followups)

    async def aget_by_horoscope(self, horoscope_id: int) -> List[HoroscopeFollowupEntity]:
        return await sync_to_async(self.get_by_horoscope)(horoscope_id)
