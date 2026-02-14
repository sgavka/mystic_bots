from typing import Optional

from asgiref.sync import sync_to_async
from django.db.models import Sum

from core.repositories.base import BaseRepository
from horoscope.entities import LLMUsageEntity
from horoscope.exceptions import LLMUsageNotFoundException
from horoscope.models import LLMUsage


class LLMUsageRepository(BaseRepository[LLMUsage, LLMUsageEntity]):
    def __init__(self):
        super().__init__(
            model=LLMUsage,
            entity=LLMUsageEntity,
            not_found_exception=LLMUsageNotFoundException,
        )

    def create_usage(
        self,
        horoscope_id: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> LLMUsageEntity:
        usage = LLMUsage.objects.create(
            horoscope_id=horoscope_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        return LLMUsageEntity.from_model(usage)

    async def acreate_usage(
        self,
        horoscope_id: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> LLMUsageEntity:
        return await sync_to_async(self.create_usage)(
            horoscope_id,
            model,
            input_tokens,
            output_tokens,
        )

    def get_by_horoscope_id(self, horoscope_id: int) -> Optional[LLMUsageEntity]:
        try:
            usage = LLMUsage.objects.get(horoscope_id=horoscope_id)
            return LLMUsageEntity.from_model(usage)
        except LLMUsage.DoesNotExist:
            return None

    async def aget_by_horoscope_id(self, horoscope_id: int) -> Optional[LLMUsageEntity]:
        return await sync_to_async(self.get_by_horoscope_id)(horoscope_id)

    def get_usage_summary(self) -> list[dict]:
        results = (
            LLMUsage.objects
            .values('model')
            .annotate(
                total_input_tokens=Sum('input_tokens'),
                total_output_tokens=Sum('output_tokens'),
                count=Sum(1),
            )
            .order_by('model')
        )
        return list(results)

    async def aget_usage_summary(self) -> list[dict]:
        return await sync_to_async(self.get_usage_summary)()
