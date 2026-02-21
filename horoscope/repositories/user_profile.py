from datetime import date, time
from typing import Optional
from config import settings
from asgiref.sync import sync_to_async

from core.repositories.base import BaseRepository
from horoscope.entities import UserProfileEntity
from horoscope.exceptions import UserProfileNotFoundException
from horoscope.models import UserProfile


class UserProfileRepository(BaseRepository[UserProfile, UserProfileEntity]):
    def __init__(self):
        super().__init__(
            model=UserProfile,
            entity=UserProfileEntity,
            not_found_exception=UserProfileNotFoundException,
        )

    def get_by_telegram_uid(self, telegram_uid: int) -> Optional[UserProfileEntity]:
        try:
            profile = UserProfile.objects.get(user_telegram_uid=telegram_uid)
            return UserProfileEntity.from_model(profile)
        except UserProfile.DoesNotExist:
            return None

    async def aget_by_telegram_uid(self, telegram_uid: int) -> Optional[UserProfileEntity]:
        return await sync_to_async(self.get_by_telegram_uid)(telegram_uid)

    def create_profile(
        self,
        telegram_uid: int,
        name: str,
        date_of_birth: str,
        place_of_birth: str,
        place_of_living: str,
        birth_time: Optional[time] = None,
        preferred_language: str = 'en',
    ) -> UserProfileEntity:
        profile = UserProfile.objects.create(
            user_telegram_uid=telegram_uid,
            name=name,
            date_of_birth=date_of_birth,
            place_of_birth=place_of_birth,
            place_of_living=place_of_living,
            birth_time=birth_time,
            preferred_language=preferred_language,
        )
        return UserProfileEntity.from_model(profile)

    async def acreate_profile(
        self,
        telegram_uid: int,
        name: str,
        date_of_birth: str,
        place_of_birth: str,
        place_of_living: str,
        birth_time: Optional[time] = None,
        preferred_language: str = 'en',
    ) -> UserProfileEntity:
        return await sync_to_async(self.create_profile)(
            telegram_uid,
            name,
            date_of_birth,
            place_of_birth,
            place_of_living,
            birth_time,
            preferred_language,
        )

    def update_language(self, telegram_uid: int, language: str) -> Optional[UserProfileEntity]:
        try:
            profile = UserProfile.objects.get(user_telegram_uid=telegram_uid)
            profile.preferred_language = language
            profile.save(update_fields=['preferred_language', 'updated_at'])
            return UserProfileEntity.from_model(profile)
        except UserProfile.DoesNotExist:
            return None

    async def aupdate_language(self, telegram_uid: int, language: str) -> Optional[UserProfileEntity]:
        return await sync_to_async(self.update_language)(telegram_uid, language)

    def update_timezone(self, telegram_uid: int, timezone: str) -> Optional[UserProfileEntity]:
        try:
            profile = UserProfile.objects.get(user_telegram_uid=telegram_uid)
            profile.timezone = timezone
            profile.save(update_fields=['timezone', 'updated_at'])
            return UserProfileEntity.from_model(profile)
        except UserProfile.DoesNotExist:
            return None

    async def aupdate_timezone(self, telegram_uid: int, timezone: str) -> Optional[UserProfileEntity]:
        return await sync_to_async(self.update_timezone)(telegram_uid, timezone)

    def update_notification_hour(
        self,
        telegram_uid: int,
        notification_hour_utc: Optional[int],
    ) -> Optional[UserProfileEntity]:
        try:
            profile = UserProfile.objects.get(user_telegram_uid=telegram_uid)
            profile.notification_hour_utc = notification_hour_utc
            profile.save(update_fields=['notification_hour_utc', 'updated_at'])
            return UserProfileEntity.from_model(profile)
        except UserProfile.DoesNotExist:
            return None

    async def aupdate_notification_hour(
        self,
        telegram_uid: int,
        notification_hour_utc: Optional[int],
    ) -> Optional[UserProfileEntity]:
        return await sync_to_async(self.update_notification_hour)(
            telegram_uid,
            notification_hour_utc,
        )

    def get_telegram_uids_by_notification_hour(self, hour_utc: int) -> list[int]:
        """Get telegram UIDs of users whose effective notification hour matches the given UTC hour."""
        result: list[int] = []
        # Users with explicit notification_hour_utc set
        explicit = list(
            UserProfile.objects.filter(
                notification_hour_utc=hour_utc,
            ).values_list('user_telegram_uid', flat=True)
        )
        result.extend(explicit)

        # Users without explicit hour — use per-language defaults (pure DB queries)
        # Find languages whose configured hour matches
        matching_langs = [
            lang for lang, hour in settings.HOROSCOPE_GENERATION_HOURS_UTC.items()
            if hour == hour_utc
        ]
        all_configured_langs = list(settings.HOROSCOPE_GENERATION_HOURS_UTC.keys())
        default_hour_matches = settings.HOROSCOPE_DEFAULT_GENERATION_HOUR_UTC == hour_utc

        # Users with a language that maps to this hour
        if matching_langs:
            lang_matches = list(
                UserProfile.objects.filter(
                    notification_hour_utc__isnull=True,
                    preferred_language__in=matching_langs,
                ).values_list('user_telegram_uid', flat=True)
            )
            result.extend(lang_matches)

        # Users whose language is NOT in the configured mapping — they use the default hour
        if default_hour_matches:
            default_matches = list(
                UserProfile.objects.filter(
                    notification_hour_utc__isnull=True,
                ).exclude(
                    preferred_language__in=all_configured_langs,
                ).values_list('user_telegram_uid', flat=True)
            )
            result.extend(default_matches)

        return result

    async def aget_telegram_uids_by_notification_hour(self, hour_utc: int) -> list[int]:
        return await sync_to_async(self.get_telegram_uids_by_notification_hour)(hour_utc)

    def get_all_telegram_uids(self) -> list[int]:
        return list(
            UserProfile.objects.values_list('user_telegram_uid', flat=True)
        )

    async def aget_all_telegram_uids(self) -> list[int]:
        return await sync_to_async(self.get_all_telegram_uids)()

    def count_created_since(self, since: date) -> int:
        return UserProfile.objects.filter(created_at__date__gte=since).count()

    async def acount_created_since(self, since: date) -> int:
        return await sync_to_async(self.count_created_since)(since)
