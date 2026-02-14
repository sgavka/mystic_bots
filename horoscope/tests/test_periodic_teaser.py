"""
Tests for the periodic teaser feature:
- generate_daily_for_all_users_task filters non-subscribers by activity window
- send_periodic_teaser_notifications_task sends extended teasers to active non-subscribers
- send_daily_horoscope_notifications_task sends only to subscribers
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.utils import timezone

from horoscope.entities import HoroscopeEntity, UserProfileEntity


def _make_profile(telegram_uid: int = 12345) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name="Test",
        date_of_birth=date(1990, 5, 15),
        place_of_birth="London",
        place_of_living="Berlin",
        preferred_language="en",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


def _make_horoscope(telegram_uid: int = 12345) -> HoroscopeEntity:
    return HoroscopeEntity(
        id=1,
        user_telegram_uid=telegram_uid,
        horoscope_type="daily",
        date=date.today(),
        full_text="Full text",
        teaser_text="Teaser",
        extended_teaser_text="Extended teaser content",
        created_at=datetime(2024, 1, 1),
    )


class TestGenerateDailyFiltersByActivity:
    @pytest.mark.django_db
    def test_skips_non_subscriber_without_recent_activity(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users_task

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_all_telegram_uids.return_value = [111]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = timezone.now() - timedelta(days=30)

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope_task') as mock_task, \
             patch('core.models.User') as MockUser:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = generate_daily_for_all_users_task()

        assert result == 0
        mock_task.delay.assert_not_called()

    @pytest.mark.django_db
    def test_includes_non_subscriber_with_recent_activity(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users_task

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_all_telegram_uids.return_value = [111]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = timezone.now() - timedelta(days=1)

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope_task') as mock_task, \
             patch('core.models.User') as MockUser:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = generate_daily_for_all_users_task()

        assert result == 1
        mock_task.delay.assert_called_once()

    @pytest.mark.django_db
    def test_always_includes_subscriber(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users_task

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_all_telegram_uids.return_value = [111]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = True

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope_task') as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = generate_daily_for_all_users_task()

        assert result == 1
        mock_task.delay.assert_called_once()

    @pytest.mark.django_db
    def test_skips_non_subscriber_with_no_last_activity(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users_task

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_all_telegram_uids.return_value = [111]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = None

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.generate_horoscope.generate_horoscope_task') as mock_task, \
             patch('core.models.User') as MockUser:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = generate_daily_for_all_users_task()

        assert result == 0
        mock_task.delay.assert_not_called()


class TestSendPeriodicTeaserNotifications:
    @pytest.mark.django_db
    def test_sends_extended_teaser_to_active_non_subscriber(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications_task

        profile = _make_profile(telegram_uid=111)
        horoscope = _make_horoscope(telegram_uid=111)

        mock_profile_repo = MagicMock()
        mock_profile_repo.all.return_value = [profile]

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.get_by_user_and_date.return_value = horoscope
        mock_horoscope_repo.get_last_sent_at.return_value = None

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = timezone.now() - timedelta(days=1)

        with patch('core.containers.container') as mock_container, \
             patch('core.models.User') as MockUser, \
             patch('horoscope.tasks.messaging.send_message', return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = send_periodic_teaser_notifications_task()

        assert result == 1
        text = mock_send.call_args[1]['text']
        assert "Extended teaser content" in text
        assert "🔒" in text
        mock_horoscope_repo.mark_sent.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    def test_skips_subscriber(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications_task

        profile = _make_profile(telegram_uid=111)

        mock_profile_repo = MagicMock()
        mock_profile_repo.all.return_value = [profile]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = True

        with patch('core.containers.container') as mock_container, \
             patch('horoscope.tasks.messaging.send_message', return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = send_periodic_teaser_notifications_task()

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    def test_skips_inactive_user(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications_task

        profile = _make_profile(telegram_uid=111)

        mock_profile_repo = MagicMock()
        mock_profile_repo.all.return_value = [profile]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = timezone.now() - timedelta(days=30)

        mock_horoscope_repo = MagicMock()

        with patch('core.containers.container') as mock_container, \
             patch('core.models.User') as MockUser, \
             patch('horoscope.tasks.messaging.send_message', return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = send_periodic_teaser_notifications_task()

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    def test_skips_recently_sent(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications_task

        profile = _make_profile(telegram_uid=111)

        mock_profile_repo = MagicMock()
        mock_profile_repo.all.return_value = [profile]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = timezone.now() - timedelta(days=1)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.get_last_sent_at.return_value = timezone.now() - timedelta(days=2)

        with patch('core.containers.container') as mock_container, \
             patch('core.models.User') as MockUser, \
             patch('horoscope.tasks.messaging.send_message', return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = send_periodic_teaser_notifications_task()

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    def test_sends_when_last_sent_exceeds_interval(self):
        from horoscope.tasks.send_periodic_teaser import send_periodic_teaser_notifications_task

        profile = _make_profile(telegram_uid=111)
        horoscope = _make_horoscope(telegram_uid=111)

        mock_profile_repo = MagicMock()
        mock_profile_repo.all.return_value = [profile]

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        mock_user = MagicMock()
        mock_user.last_activity = timezone.now() - timedelta(days=1)

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.get_last_sent_at.return_value = timezone.now() - timedelta(
            days=settings.HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS + 1,
        )
        mock_horoscope_repo.get_by_user_and_date.return_value = horoscope

        with patch('core.containers.container') as mock_container, \
             patch('core.models.User') as MockUser, \
             patch('horoscope.tasks.messaging.send_message', return_value=True) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            MockUser.objects.get.return_value = mock_user

            result = send_periodic_teaser_notifications_task()

        assert result == 1
        mock_send.assert_called_once()
