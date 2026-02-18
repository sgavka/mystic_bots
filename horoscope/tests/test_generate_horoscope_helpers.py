"""
Tests for horoscope/tasks/generate_horoscope.py — _send_daily_horoscope and _send_first_horoscope helpers.
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from horoscope.entities import UserProfileEntity


def _make_profile(
    telegram_uid: int = 12345,
    preferred_language: str = "en",
) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name="Test",
        date_of_birth=date(1990, 5, 15),
        place_of_birth="London",
        place_of_living="Berlin",
        preferred_language=preferred_language,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


class TestSendDailyHoroscope:
    @pytest.mark.django_db
    async def test_subscriber_receives_full_text(self):
        from horoscope.tasks.generate_horoscope import _send_daily_horoscope

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_sent = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=_make_profile())

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo

            await _send_daily_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Full horoscope text here",
                teaser_text="Teaser only",
            )

        text = mock_send.call_args[1]['text']
        assert "Full horoscope text here" in text
        assert "just type your message" in text
        assert mock_send.call_args[1]['reply_markup'] is None
        mock_horoscope_repo.amark_sent.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_non_subscriber_receives_teaser_with_subscribe_link(self):
        from horoscope.tasks.generate_horoscope import _send_daily_horoscope

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_sent = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=_make_profile())

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo

            await _send_daily_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Full horoscope text here",
                teaser_text="Teaser only",
            )

        text = mock_send.call_args[1]['text']
        assert "Teaser only" in text
        assert "\U0001f512" in text
        assert mock_send.call_args[1]['reply_markup'] is not None
        mock_horoscope_repo.amark_sent.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_failed_send_marks_horoscope_as_failed(self):
        from horoscope.tasks.generate_horoscope import _send_daily_horoscope

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_failed_to_send = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=_make_profile())

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=False):
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo

            await _send_daily_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Full text",
                teaser_text="Teaser",
            )

        mock_horoscope_repo.amark_sent.assert_not_called()
        mock_horoscope_repo.amark_failed_to_send.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_uses_profile_language_for_translation(self):
        from horoscope.tasks.generate_horoscope import _send_daily_horoscope

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_sent = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(
            return_value=_make_profile(preferred_language="ru"),
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo

            await _send_daily_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Full text",
                teaser_text="Teaser",
            )

        mock_send.assert_called_once()


class TestSendFirstHoroscope:
    @pytest.mark.django_db
    async def test_sends_first_horoscope_success(self):
        from horoscope.tasks.generate_horoscope import _send_first_horoscope

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_sent = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=_make_profile())

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            await _send_first_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Your personalized horoscope",
            )

        text = mock_send.call_args[1]['text']
        assert "Your personalized horoscope" in text
        assert "\U0001f52e" in text
        mock_horoscope_repo.amark_sent.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_sends_first_horoscope_failure(self):
        from horoscope.tasks.generate_horoscope import _send_first_horoscope

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_failed_to_send = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=_make_profile())

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=False):
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            await _send_first_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Your personalized horoscope",
            )

        mock_horoscope_repo.amark_sent.assert_not_called()
        mock_horoscope_repo.amark_failed_to_send.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_defaults_to_en_when_no_profile(self):
        from horoscope.tasks.generate_horoscope import _send_first_horoscope

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.amark_sent = AsyncMock()

        mock_user_profile_repo = MagicMock()
        mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=None)

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            await _send_first_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                horoscope_id=42,
                full_text="Horoscope text",
            )

        mock_send.assert_called_once()
        text = mock_send.call_args[1]['text']
        assert "Horoscope text" in text
