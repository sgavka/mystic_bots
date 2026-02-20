import logging
from datetime import date
from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async

from horoscope.entities import HoroscopeEntity, UserProfileEntity
from horoscope.enums import HoroscopeType
from horoscope.utils import get_zodiac_sign

if TYPE_CHECKING:
    from horoscope.repositories import HoroscopeRepository, LLMUsageRepository, UserProfileRepository

logger = logging.getLogger(__name__)


class HoroscopeService:
    def __init__(
        self,
        horoscope_repo: "HoroscopeRepository",
        user_profile_repo: "UserProfileRepository",
        llm_usage_repo: "LLMUsageRepository",
    ):
        self.horoscope_repo = horoscope_repo
        self.user_profile_repo = user_profile_repo
        self.llm_usage_repo = llm_usage_repo

    def generate_for_user(
        self,
        telegram_uid: int,
        target_date: date,
        horoscope_type: HoroscopeType = HoroscopeType.DAILY,
    ) -> HoroscopeEntity:
        existing = self.horoscope_repo.get_by_user_and_date(
            telegram_uid=telegram_uid,
            target_date=target_date,
        )
        if existing:
            return existing

        profile = self.user_profile_repo.get_by_telegram_uid(telegram_uid)
        if not profile:
            raise ValueError(f"No profile found for user {telegram_uid}")

        full_text, teaser_text, extended_teaser_text, llm_result = self._generate_text(
            profile=profile,
            target_date=target_date,
            language=profile.preferred_language,
        )

        horoscope = self.horoscope_repo.create_horoscope(
            telegram_uid=telegram_uid,
            horoscope_type=horoscope_type,
            target_date=target_date,
            full_text=full_text,
            teaser_text=teaser_text,
            extended_teaser_text=extended_teaser_text,
        )

        self.llm_usage_repo.create_usage(
            horoscope_id=horoscope.id,
            model=llm_result.model,
            input_tokens=llm_result.input_tokens,
            output_tokens=llm_result.output_tokens,
        )

        logger.info(f"Generated {horoscope_type} horoscope for user {telegram_uid} on {target_date}")
        return horoscope

    def _generate_text(
        self,
        profile: UserProfileEntity,
        target_date: date,
        language: str = 'en',
    ) -> tuple:
        from horoscope.services.llm import LLMService

        llm_service = LLMService()
        sign = get_zodiac_sign(profile.date_of_birth)
        result = llm_service.generate_horoscope_text(
            zodiac_sign=sign,
            name=profile.name,
            date_of_birth=profile.date_of_birth,
            place_of_birth=profile.place_of_birth,
            place_of_living=profile.place_of_living,
            target_date=target_date,
            language=language,
            birth_time=profile.birth_time,
        )
        return result.full_text, result.teaser_text, result.extended_teaser_text, result

    async def agenerate_for_user(
        self,
        telegram_uid: int,
        target_date: date,
        horoscope_type: HoroscopeType = HoroscopeType.DAILY,
    ) -> HoroscopeEntity:
        return await sync_to_async(self.generate_for_user)(
            telegram_uid,
            target_date,
            horoscope_type,
        )
