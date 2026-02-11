"""
Tests for HoroscopeService class methods:
generate_for_user, _generate_text, agenerate_for_user.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from horoscope.entities import HoroscopeEntity, UserProfileEntity

# Patch target: container is imported at module level in horoscope.services.horoscope
CONTAINER_PATCH = 'horoscope.services.horoscope.container'


def _make_profile(telegram_uid: int = 12345) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name="Test User",
        date_of_birth=date(1990, 5, 15),
        place_of_birth="London",
        place_of_living="Berlin",
        preferred_language="en",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


def _make_horoscope(telegram_uid: int = 12345) -> HoroscopeEntity:
    return HoroscopeEntity(
        id=42,
        user_telegram_uid=telegram_uid,
        horoscope_type="daily",
        date=date(2024, 6, 15),
        full_text="Full horoscope text",
        teaser_text="Teaser...",
        created_at=datetime(2024, 1, 1),
    )


class TestHoroscopeServiceGenerateForUser:
    def _make_service(self, horoscope_repo=None, user_profile_repo=None):
        with patch(CONTAINER_PATCH) as mock_container:
            mock_container.horoscope.horoscope_repository.return_value = (
                horoscope_repo or MagicMock()
            )
            mock_container.horoscope.user_profile_repository.return_value = (
                user_profile_repo or MagicMock()
            )
            from horoscope.services.horoscope import HoroscopeService
            return HoroscopeService()

    def test_returns_existing_horoscope(self):
        existing = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = existing

        service = self._make_service(horoscope_repo=horoscope_repo)
        result = service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        assert result == existing
        horoscope_repo.create_horoscope.assert_not_called()

    def test_raises_when_no_profile(self):
        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = None

        user_profile_repo = MagicMock()
        user_profile_repo.get_by_telegram_uid.return_value = None

        service = self._make_service(
            horoscope_repo=horoscope_repo,
            user_profile_repo=user_profile_repo,
        )

        with pytest.raises(ValueError, match="No profile found"):
            service.generate_for_user(
                telegram_uid=99999,
                target_date=date(2024, 6, 15),
            )

    def test_generates_new_horoscope(self):
        profile = _make_profile()
        new_horoscope = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = None
        horoscope_repo.create_horoscope.return_value = new_horoscope

        user_profile_repo = MagicMock()
        user_profile_repo.get_by_telegram_uid.return_value = profile

        service = self._make_service(
            horoscope_repo=horoscope_repo,
            user_profile_repo=user_profile_repo,
        )

        service._generate_text = MagicMock(return_value=("Full text", "Teaser"))

        result = service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        assert result == new_horoscope
        horoscope_repo.create_horoscope.assert_called_once()

    def test_generates_with_first_type(self):
        profile = _make_profile()
        new_horoscope = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = None
        horoscope_repo.create_horoscope.return_value = new_horoscope

        user_profile_repo = MagicMock()
        user_profile_repo.get_by_telegram_uid.return_value = profile

        service = self._make_service(
            horoscope_repo=horoscope_repo,
            user_profile_repo=user_profile_repo,
        )

        service._generate_text = MagicMock(return_value=("Full text", "Teaser"))

        result = service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
            horoscope_type="first",
        )

        assert result == new_horoscope
        call_kwargs = horoscope_repo.create_horoscope.call_args[1]
        assert call_kwargs['horoscope_type'] == 'first'

    def test_passes_profile_language_to_generate_text(self):
        profile_ru = UserProfileEntity(
            user_telegram_uid=12345,
            name="Test",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="Moscow",
            place_of_living="Berlin",
            preferred_language="ru",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        new_horoscope = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = None
        horoscope_repo.create_horoscope.return_value = new_horoscope

        user_profile_repo = MagicMock()
        user_profile_repo.get_by_telegram_uid.return_value = profile_ru

        service = self._make_service(
            horoscope_repo=horoscope_repo,
            user_profile_repo=user_profile_repo,
        )

        service._generate_text = MagicMock(return_value=("Full text", "Teaser"))

        service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        service._generate_text.assert_called_once_with(
            profile=profile_ru,
            target_date=date(2024, 6, 15),
            language="ru",
        )


class TestHoroscopeServiceGenerateText:
    def _make_service(self):
        with patch(CONTAINER_PATCH) as mock_container:
            mock_container.horoscope.horoscope_repository.return_value = MagicMock()
            mock_container.horoscope.user_profile_repository.return_value = MagicMock()
            from horoscope.services.horoscope import HoroscopeService
            return HoroscopeService()

    def test_uses_llm_when_configured(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = True
        mock_llm.generate_horoscope_text.return_value = ("LLM full", "LLM teaser")

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, teaser = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert full == "LLM full"
        assert teaser == "LLM teaser"

    def test_falls_back_to_template_when_llm_fails(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = True
        mock_llm.generate_horoscope_text.side_effect = Exception("LLM error")

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, teaser = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert len(full) > 0
        assert len(teaser) > 0
        assert "Taurus" in full

    def test_falls_back_to_template_when_llm_not_configured(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = False

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, _ = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert len(full) > 0
        assert "Taurus" in full
        mock_llm.generate_horoscope_text.assert_not_called()

    def test_respects_language_parameter(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = False

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, _ = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="ru",
            )

        assert "Гороскоп" in full


class TestHoroscopeServiceAsync:
    @pytest.mark.asyncio
    async def test_agenerate_for_user(self):
        existing = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = existing

        with patch(CONTAINER_PATCH) as mock_container:
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo
            mock_container.horoscope.user_profile_repository.return_value = MagicMock()

            from horoscope.services.horoscope import HoroscopeService
            service = HoroscopeService()

        result = await service.agenerate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        assert result == existing
