"""
Tests for horoscope/tasks/generate_horoscope.py — _send_first_horoscope and generate_and_send_horoscope helpers.
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.utils import timezone

from horoscope.entities import SubscriptionEntity, UserProfileEntity
from horoscope.enums import HoroscopeType, SubscriptionStatus


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


def _make_subscription(
    expires_at: datetime | None = None,
    status: str = SubscriptionStatus.EXPIRED,
) -> SubscriptionEntity:
    return SubscriptionEntity(
        id=1,
        user_telegram_uid=12345,
        status=status,
        started_at=datetime(2024, 1, 1),
        expires_at=expires_at,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


def _setup_generate_mocks(
    has_subscription: bool = True,
    latest_subscription: SubscriptionEntity | None = None,
    profile: UserProfileEntity | None = None,
) -> dict:
    """Set up common mocks for generate_and_send_horoscope tests."""
    mock_horoscope = MagicMock()
    mock_horoscope.id = 42
    mock_horoscope.full_text = "Full horoscope text here"
    mock_horoscope.teaser_text = "Teaser text"
    mock_horoscope.extended_teaser_text = "Extended teaser text"

    mock_horoscope_repo = MagicMock()
    mock_horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=mock_horoscope)
    mock_horoscope_repo.amark_sent = AsyncMock()
    mock_horoscope_repo.amark_failed_to_send = AsyncMock()

    mock_user_profile_repo = MagicMock()
    mock_user_profile_repo.aget_by_telegram_uid = AsyncMock(
        return_value=profile or _make_profile(),
    )

    mock_subscription_repo = MagicMock()
    mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=has_subscription)
    mock_subscription_repo.aget_latest_by_user = AsyncMock(return_value=latest_subscription)

    return {
        'horoscope': mock_horoscope,
        'horoscope_repo': mock_horoscope_repo,
        'user_profile_repo': mock_user_profile_repo,
        'subscription_repo': mock_subscription_repo,
    }


class TestGenerateAndSendHoroscope:
    @pytest.mark.django_db
    async def test_subscriber_gets_full_text(self):
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        mocks = _setup_generate_mocks(has_subscription=True)

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock) as mock_generate, \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        mock_generate.assert_called_once_with(
            bot=mock_bot,
            telegram_uid=12345,
            target_date="2024-06-15",
            horoscope_type=HoroscopeType.DAILY,
        )
        text = mock_send.call_args[1]['text']
        assert "Full horoscope text here" in text
        assert "just type your message" in text
        mocks['horoscope_repo'].amark_sent.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_non_subscriber_phase1_gets_teaser(self):
        """Non-subscriber in Phase 1 gets short teaser text."""
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        profile = _make_profile()
        profile.created_at = timezone.now() - timedelta(days=2)

        mocks = _setup_generate_mocks(
            has_subscription=False,
            latest_subscription=None,
            profile=profile,
        )

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        text = mock_send.call_args[1]['text']
        assert "Teaser text" in text
        assert "Full horoscope text here" not in text
        assert "\U0001f512" in text

    @pytest.mark.django_db
    async def test_non_subscriber_phase2_gets_extended_teaser(self):
        """Non-subscriber in Phase 2 gets extended teaser text."""
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        profile = _make_profile()
        profile.created_at = timezone.now() - timedelta(days=60)

        mocks = _setup_generate_mocks(
            has_subscription=False,
            latest_subscription=None,
            profile=profile,
        )

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        text = mock_send.call_args[1]['text']
        assert "Extended teaser text" in text
        assert "\U0001f512" in text

    @pytest.mark.django_db
    async def test_non_subscriber_with_expired_sub_uses_expires_at(self):
        """Non-subscriber with expired subscription uses expires_at as Phase 1 reference."""
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        profile = _make_profile()
        profile.created_at = timezone.now() - timedelta(days=60)

        subscription = _make_subscription(
            expires_at=timezone.now() - timedelta(days=2),
        )
        mocks = _setup_generate_mocks(
            has_subscription=False,
            latest_subscription=subscription,
            profile=profile,
        )

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        text = mock_send.call_args[1]['text']
        assert "Teaser text" in text
        assert "Full horoscope text here" not in text

    @pytest.mark.django_db
    async def test_non_subscriber_sends_with_subscribe_keyboard(self):
        """Non-subscriber gets subscribe keyboard."""
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        profile = _make_profile()
        profile.created_at = timezone.now() - timedelta(days=2)

        mocks = _setup_generate_mocks(
            has_subscription=False,
            latest_subscription=None,
            profile=profile,
        )

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        assert mock_send.call_args[1]['reply_markup'] is not None

    @pytest.mark.django_db
    async def test_marks_failed_when_send_fails(self):
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        mocks = _setup_generate_mocks(has_subscription=True)

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=False):
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        mocks['horoscope_repo'].amark_sent.assert_not_called()
        mocks['horoscope_repo'].amark_failed_to_send.assert_called_once_with(horoscope_id=42)

    @pytest.mark.django_db
    async def test_returns_early_when_horoscope_not_found(self):
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=None)

        mock_user_profile_repo = MagicMock()

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_user_profile_repo

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        mock_send.assert_not_called()

    @pytest.mark.django_db
    async def test_uses_profile_language(self):
        from horoscope.tasks.generate_horoscope import generate_and_send_horoscope

        mocks = _setup_generate_mocks(
            has_subscription=True,
            profile=_make_profile(preferred_language="ru"),
        )

        mock_bot = MagicMock()

        with patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock), \
             patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['user_profile_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']

            await generate_and_send_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
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
