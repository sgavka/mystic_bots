"""
Tests for HoroscopeService class methods:
generate_for_user, _generate_text, agenerate_for_user.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from horoscope.entities import HoroscopeEntity, UserProfileEntity
from horoscope.services.horoscope import HoroscopeService
from horoscope.services.llm import LLMResult


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
    def _make_service(self, horoscope_repo=None, user_profile_repo=None, llm_usage_repo=None):
        return HoroscopeService(
            horoscope_repo=horoscope_repo or MagicMock(),
            user_profile_repo=user_profile_repo or MagicMock(),
            llm_usage_repo=llm_usage_repo or MagicMock(),
        )

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

        service._generate_text = MagicMock(return_value=("Full text", "Teaser", "Extended teaser", None))

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

        service._generate_text = MagicMock(return_value=("Full text", "Teaser", "Extended teaser", None))

        result = service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
            horoscope_type="first",
        )

        assert result == new_horoscope
        call_kwargs = horoscope_repo.create_horoscope.call_args[1]
        assert call_kwargs['horoscope_type'] == 'first'

    def test_saves_llm_usage_when_llm_used(self):
        profile = _make_profile()
        new_horoscope = _make_horoscope()
        llm_result = LLMResult(
            full_text="LLM full",
            teaser_text="LLM teaser",
            extended_teaser_text="LLM extended teaser",
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
        )

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = None
        horoscope_repo.create_horoscope.return_value = new_horoscope

        user_profile_repo = MagicMock()
        user_profile_repo.get_by_telegram_uid.return_value = profile

        llm_usage_repo = MagicMock()

        service = self._make_service(
            horoscope_repo=horoscope_repo,
            user_profile_repo=user_profile_repo,
            llm_usage_repo=llm_usage_repo,
        )

        service._generate_text = MagicMock(return_value=("LLM full", "LLM teaser", "LLM extended teaser", llm_result))

        service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        llm_usage_repo.create_usage.assert_called_once_with(
            horoscope_id=new_horoscope.id,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
        )

    def test_does_not_save_llm_usage_when_template_used(self):
        profile = _make_profile()
        new_horoscope = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = None
        horoscope_repo.create_horoscope.return_value = new_horoscope

        user_profile_repo = MagicMock()
        user_profile_repo.get_by_telegram_uid.return_value = profile

        llm_usage_repo = MagicMock()

        service = self._make_service(
            horoscope_repo=horoscope_repo,
            user_profile_repo=user_profile_repo,
            llm_usage_repo=llm_usage_repo,
        )

        service._generate_text = MagicMock(return_value=("Full text", "Teaser", "Extended teaser", None))

        service.generate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        llm_usage_repo.create_usage.assert_not_called()

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

        service._generate_text = MagicMock(return_value=("Full text", "Teaser", "Extended teaser", None))

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
        return HoroscopeService(
            horoscope_repo=MagicMock(),
            user_profile_repo=MagicMock(),
            llm_usage_repo=MagicMock(),
        )

    def test_uses_llm_when_configured(self):
        service = self._make_service()
        profile = _make_profile()

        llm_result = LLMResult(
            full_text="LLM full",
            teaser_text="LLM teaser",
            extended_teaser_text="LLM extended teaser",
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
        )

        mock_llm = MagicMock()
        mock_llm.is_configured = True
        mock_llm.generate_horoscope_text.return_value = llm_result

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, teaser, extended_teaser, result = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert full == "LLM full"
        assert teaser == "LLM teaser"
        assert result is not None
        assert result.model == "gpt-4o-mini"
        assert result.input_tokens == 100
        assert result.output_tokens == 200

    def test_falls_back_to_template_when_llm_fails(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = True
        mock_llm.generate_horoscope_text.side_effect = Exception("LLM error")

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, teaser, extended_teaser, result = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert len(full) > 0
        assert len(teaser) > 0
        assert "Taurus" in full
        assert result is None

    def test_falls_back_to_template_when_llm_not_configured(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = False

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, _, _, result = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert len(full) > 0
        assert "Taurus" in full
        assert result is None
        mock_llm.generate_horoscope_text.assert_not_called()

    def test_respects_language_parameter(self):
        service = self._make_service()
        profile = _make_profile()

        mock_llm = MagicMock()
        mock_llm.is_configured = False

        with patch('horoscope.services.llm.LLMService', return_value=mock_llm):
            full, _, _, result = service._generate_text(
                profile=profile,
                target_date=date(2024, 6, 15),
                language="ru",
            )

        assert "Гороскоп" in full
        assert result is None


class TestHoroscopeServiceAsync:
    @pytest.mark.asyncio
    async def test_agenerate_for_user(self):
        existing = _make_horoscope()

        horoscope_repo = MagicMock()
        horoscope_repo.get_by_user_and_date.return_value = existing

        service = HoroscopeService(
            horoscope_repo=horoscope_repo,
            user_profile_repo=MagicMock(),
            llm_usage_repo=MagicMock(),
        )

        result = await service.agenerate_for_user(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        assert result == existing
