"""
Tests for the periodic teaser feature:
- generate_daily_for_all_users filters non-subscribers by activity window
- send_periodic_teaser_notifications uses two-phase teaser sending:
  - Phase 1 (first N days): send short teaser daily
  - Phase 2 (after N days): send extended teaser every M days
- send_daily_horoscope_notifications sends only to subscribers
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.conf import settings
from django.utils import timezone

from core.entities import UserEntity
from horoscope.entities import HoroscopeEntity, UserProfileEntity
from horoscope.enums import HoroscopeType


def _make_profile(
    telegram_uid: int = 12345,
    created_at: datetime | None = None,
) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name="Test",
        date_of_birth=date(1990, 5, 15),
        place_of_birth="London",
        place_of_living="Berlin",
        preferred_language="en",
        created_at=created_at or datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


def _make_horoscope(telegram_uid: int = 12345) -> HoroscopeEntity:
    return HoroscopeEntity(
        id=1,
        user_telegram_uid=telegram_uid,
        horoscope_type=HoroscopeType.DAILY,
        date=date.today(),
        full_text="Full text",
        teaser_text="Teaser",
        extended_teaser_text="Extended teaser content",
        created_at=datetime(2024, 1, 1),
    )


def _make_user_entity(
    telegram_uid: int = 12345,
    last_activity: datetime | None = None,
) -> UserEntity:
    return UserEntity(
        telegram_uid=telegram_uid,
        username="test",
        first_name="Test",
        last_name="User",
        language_code="en",
        is_premium=False,
        last_activity=last_activity,
    )


class TestGenerateDailyFiltersByActivity:
    @pytest.mark.django_db
    async def test_skips_non_subscriber_without_recent_activity(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_telegram_uids_by_notification_hour = AsyncMock(return_value=[111])  # used by generate task

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        user_entity = _make_user_entity(
            telegram_uid=111,
            last_activity=timezone.now() - timedelta(days=30),
        )
        mock_user_repo = MagicMock()
        mock_user_repo.aget = AsyncMock(return_value=user_entity)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock) as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.core.user_repository.return_value = mock_user_repo

            result = await generate_daily_for_all_users(mock_bot)

        assert result == 0
        mock_task.assert_not_called()

    @pytest.mark.django_db
    async def test_includes_non_subscriber_with_recent_activity(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_telegram_uids_by_notification_hour = AsyncMock(return_value=[111])  # used by generate task

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        user_entity = _make_user_entity(
            telegram_uid=111,
            last_activity=timezone.now() - timedelta(days=1),
        )
        mock_user_repo = MagicMock()
        mock_user_repo.aget = AsyncMock(return_value=user_entity)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock) as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.core.user_repository.return_value = mock_user_repo

            result = await generate_daily_for_all_users(mock_bot)

        assert result == 1
        mock_task.assert_called_once()

    @pytest.mark.django_db
    async def test_always_includes_subscriber(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_telegram_uids_by_notification_hour = AsyncMock(return_value=[111])  # used by generate task

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock) as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = await generate_daily_for_all_users(mock_bot)

        assert result == 1
        mock_task.assert_called_once()

    @pytest.mark.django_db
    async def test_skips_non_subscriber_with_no_last_activity(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_telegram_uids_by_notification_hour = AsyncMock(return_value=[111])  # used by generate task

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        user_entity = _make_user_entity(
            telegram_uid=111,
            last_activity=None,
        )
        mock_user_repo = MagicMock()
        mock_user_repo.aget = AsyncMock(return_value=user_entity)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope', new_callable=AsyncMock) as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.core.user_repository.return_value = mock_user_repo

            result = await generate_daily_for_all_users(mock_bot)

        assert result == 0
        mock_task.assert_not_called()


def _setup_common_mocks(
    telegram_uid: int = 111,
    profile_created_at: datetime | None = None,
    last_activity: datetime | None = None,
    last_sent_at: datetime | None = None,
    horoscope: HoroscopeEntity | None = None,
) -> dict:
    """Set up common mocks for send_periodic_teaser_notifications tests."""
    if last_activity is None:
        last_activity = timezone.now() - timedelta(days=1)

    profile = _make_profile(
        telegram_uid=telegram_uid,
        created_at=profile_created_at or timezone.now() - timedelta(days=1),
    )
    if horoscope is None:
        horoscope = _make_horoscope(telegram_uid=telegram_uid)

    mock_profile_repo = MagicMock()
    mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)

    mock_horoscope_repo = MagicMock()
    mock_horoscope_repo.aget_unsent_telegram_uids_for_date = AsyncMock(return_value=[telegram_uid])
    mock_horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
    mock_horoscope_repo.aget_last_sent_at = AsyncMock(return_value=last_sent_at)
    mock_horoscope_repo.amark_sent = AsyncMock()
    mock_horoscope_repo.amark_failed_to_send = AsyncMock()

    mock_subscription_repo = MagicMock()
    mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

    user_entity = _make_user_entity(
        telegram_uid=telegram_uid,
        last_activity=last_activity,
    )
    mock_user_repo = MagicMock()
    mock_user_repo.aget = AsyncMock(return_value=user_entity)

    return {
        'profile_repo': mock_profile_repo,
        'horoscope_repo': mock_horoscope_repo,
        'subscription_repo': mock_subscription_repo,
        'user_repo': mock_user_repo,
    }


class TestSendPeriodicTeaserNotifications:
    @pytest.mark.django_db
    async def test_phase1_sends_short_teaser_for_new_user(self):
        """Users in first HOROSCOPE_TEASER_DAILY_DAYS days get short teaser."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=2),
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 1
        text = mock_send.call_args[1]['text']
        assert "Teaser" in text
        assert "Extended teaser content" not in text
        assert "\U0001f512" in text
        mocks['horoscope_repo'].amark_sent.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    async def test_phase1_sends_on_boundary_day(self):
        """User on exactly HOROSCOPE_TEASER_DAILY_DAYS day still gets short teaser."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=settings.HOROSCOPE_TEASER_DAILY_DAYS),
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 1
        text = mock_send.call_args[1]['text']
        assert "Teaser" in text
        assert "Extended teaser content" not in text

    @pytest.mark.django_db
    async def test_phase2_sends_extended_teaser_when_interval_exceeded(self):
        """Users past daily phase get extended teaser when interval has passed."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=20),
            last_sent_at=timezone.now() - timedelta(
                days=settings.HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS + 1,
            ),
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 1
        text = mock_send.call_args[1]['text']
        assert "Extended teaser content" in text
        assert "\U0001f512" in text
        mocks['horoscope_repo'].amark_sent.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    async def test_phase2_sends_when_never_sent_before(self):
        """Users past daily phase with no prior sends get extended teaser."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=20),
            last_sent_at=None,
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 1
        text = mock_send.call_args[1]['text']
        assert "Extended teaser content" in text

    @pytest.mark.django_db
    async def test_phase2_skips_when_recently_sent(self):
        """Users past daily phase should be skipped if sent within interval."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=20),
            last_sent_at=timezone.now() - timedelta(days=2),
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    async def test_skips_subscriber(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.aget_unsent_telegram_uids_for_date = AsyncMock(return_value=[111])

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    async def test_skips_inactive_user(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.aget_unsent_telegram_uids_for_date = AsyncMock(return_value=[111])

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        user_entity = _make_user_entity(
            telegram_uid=111,
            last_activity=timezone.now() - timedelta(days=30),
        )
        mock_user_repo = MagicMock()
        mock_user_repo.aget = AsyncMock(return_value=user_entity)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.core.user_repository.return_value = mock_user_repo

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    async def test_skips_already_sent_horoscope(self):
        """Horoscopes that already have sent_at set should not be sent again."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        horoscope = HoroscopeEntity(
            id=1,
            user_telegram_uid=111,
            horoscope_type=HoroscopeType.DAILY,
            date=date.today(),
            full_text="Full text",
            teaser_text="Teaser",
            extended_teaser_text="Extended teaser content",
            sent_at=timezone.now(),
            created_at=datetime(2024, 1, 1),
        )

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=2),
            horoscope=horoscope,
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    async def test_marks_failed_to_send_on_failure(self):
        """When send_message returns False, mark horoscope as failed."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        mocks = _setup_common_mocks(
            profile_created_at=timezone.now() - timedelta(days=2),
        )

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=False):
            mock_container.horoscope.user_profile_repository.return_value = mocks['profile_repo']
            mock_container.horoscope.horoscope_repository.return_value = mocks['horoscope_repo']
            mock_container.horoscope.subscription_repository.return_value = mocks['subscription_repo']
            mock_container.core.user_repository.return_value = mocks['user_repo']

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 0
        mocks['horoscope_repo'].amark_failed_to_send.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    async def test_skips_user_without_profile(self):
        """Users without profile should be skipped."""
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications

        horoscope = _make_horoscope(telegram_uid=111)

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=None)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.aget_unsent_telegram_uids_for_date = AsyncMock(return_value=[111])
        mock_horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        user_entity = _make_user_entity(
            telegram_uid=111,
            last_activity=timezone.now() - timedelta(days=1),
        )
        mock_user_repo = MagicMock()
        mock_user_repo.aget = AsyncMock(return_value=user_entity)

        mock_bot = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', new_callable=AsyncMock, return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.core.user_repository.return_value = mock_user_repo

            result = await send_periodic_teaser_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()
