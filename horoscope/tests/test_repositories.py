"""
Tests for horoscope repositories.
Covers UserProfileRepository, HoroscopeRepository, SubscriptionRepository.
"""

from datetime import date, timedelta

import pytest
from django.utils import timezone

from horoscope.entities import HoroscopeEntity, SubscriptionEntity, UserProfileEntity
from horoscope.enums import SubscriptionStatus
from horoscope.models import Horoscope, Subscription, UserProfile
from horoscope.repositories.horoscope import HoroscopeRepository
from horoscope.repositories.subscription import SubscriptionRepository
from horoscope.repositories.user_profile import UserProfileRepository


@pytest.mark.django_db
class TestUserProfileRepository:
    def setup_method(self):
        self.repo = UserProfileRepository()

    def test_get_by_telegram_uid_found(self):
        UserProfile.objects.create(
            user_telegram_uid=12345,
            name="Alice",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
        )

        result = self.repo.get_by_telegram_uid(12345)

        assert result is not None
        assert isinstance(result, UserProfileEntity)
        assert result.name == "Alice"
        assert result.user_telegram_uid == 12345

    def test_get_by_telegram_uid_not_found(self):
        result = self.repo.get_by_telegram_uid(99999)
        assert result is None

    def test_create_profile(self):
        result = self.repo.create_profile(
            telegram_uid=12345,
            name="Bob",
            date_of_birth="1985-03-20",
            place_of_birth="Paris",
            place_of_living="Tokyo",
        )

        assert isinstance(result, UserProfileEntity)
        assert result.name == "Bob"
        assert result.user_telegram_uid == 12345
        assert result.preferred_language == "en"
        assert UserProfile.objects.filter(user_telegram_uid=12345).exists()

    def test_create_profile_with_language(self):
        result = self.repo.create_profile(
            telegram_uid=12345,
            name="Ivan",
            date_of_birth="1985-03-20",
            place_of_birth="Moscow",
            place_of_living="Berlin",
            preferred_language="ru",
        )

        assert result.preferred_language == "ru"

    def test_update_language_found(self):
        UserProfile.objects.create(
            user_telegram_uid=12345,
            name="Alice",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="en",
        )

        result = self.repo.update_language(telegram_uid=12345, language="de")

        assert result is not None
        assert result.preferred_language == "de"

    def test_update_language_not_found(self):
        result = self.repo.update_language(telegram_uid=99999, language="de")
        assert result is None

    def test_get_all_telegram_uids(self):
        UserProfile.objects.create(
            user_telegram_uid=111,
            name="A",
            date_of_birth=date(1990, 1, 1),
            place_of_birth="X",
            place_of_living="Y",
        )
        UserProfile.objects.create(
            user_telegram_uid=222,
            name="B",
            date_of_birth=date(1991, 1, 1),
            place_of_birth="X",
            place_of_living="Y",
        )

        uids = self.repo.get_all_telegram_uids()

        assert set(uids) == {111, 222}

    def test_get_all_telegram_uids_empty(self):
        uids = self.repo.get_all_telegram_uids()
        assert uids == []


@pytest.mark.django_db
class TestHoroscopeRepository:
    def setup_method(self):
        self.repo = HoroscopeRepository()

    def test_get_by_user_and_date_found(self):
        Horoscope.objects.create(
            user_telegram_uid=12345,
            horoscope_type="daily",
            date=date(2024, 6, 15),
            full_text="Full text",
            teaser_text="Teaser",
        )

        result = self.repo.get_by_user_and_date(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )

        assert result is not None
        assert isinstance(result, HoroscopeEntity)
        assert result.full_text == "Full text"
        assert result.teaser_text == "Teaser"

    def test_get_by_user_and_date_not_found(self):
        result = self.repo.get_by_user_and_date(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
        )
        assert result is None

    def test_get_by_user_and_date_wrong_date(self):
        Horoscope.objects.create(
            user_telegram_uid=12345,
            horoscope_type="daily",
            date=date(2024, 6, 15),
            full_text="Full text",
            teaser_text="Teaser",
        )

        result = self.repo.get_by_user_and_date(
            telegram_uid=12345,
            target_date=date(2024, 6, 16),
        )
        assert result is None

    def test_create_horoscope(self):
        result = self.repo.create_horoscope(
            telegram_uid=12345,
            horoscope_type="daily",
            target_date=date(2024, 6, 15),
            full_text="Generated horoscope",
            teaser_text="Preview...",
        )

        assert isinstance(result, HoroscopeEntity)
        assert result.full_text == "Generated horoscope"
        assert result.teaser_text == "Preview..."
        assert Horoscope.objects.filter(user_telegram_uid=12345).exists()


@pytest.mark.django_db
class TestSubscriptionRepository:
    def setup_method(self):
        self.repo = SubscriptionRepository()

    def test_get_active_by_user_found(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        result = self.repo.get_active_by_user(12345)

        assert result is not None
        assert isinstance(result, SubscriptionEntity)
        assert result.user_telegram_uid == 12345

    def test_get_active_by_user_not_found(self):
        result = self.repo.get_active_by_user(99999)
        assert result is None

    def test_get_active_by_user_expired_status(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.EXPIRED,
            expires_at=timezone.now() - timedelta(days=1),
        )

        result = self.repo.get_active_by_user(12345)
        assert result is None

    def test_has_active_subscription_true(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        assert self.repo.has_active_subscription(12345) is True

    def test_has_active_subscription_false(self):
        assert self.repo.has_active_subscription(99999) is False

    def test_activate_or_renew_new(self):
        result = self.repo.activate_or_renew(
            telegram_uid=12345,
            duration_days=30,
        )

        assert isinstance(result, SubscriptionEntity)
        assert result.user_telegram_uid == 12345
        assert Subscription.objects.filter(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
        ).exists()

    def test_activate_or_renew_existing(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=5),
        )

        result = self.repo.activate_or_renew(
            telegram_uid=12345,
            duration_days=30,
        )

        assert result is not None
        assert Subscription.objects.filter(user_telegram_uid=12345).count() == 1

    def test_activate_or_renew_with_payment_charge(self):
        result = self.repo.activate_or_renew(
            telegram_uid=12345,
            duration_days=30,
            payment_charge_id="charge_abc",
        )

        assert result.telegram_payment_charge_id == "charge_abc"

    def test_cancel_active_success(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        result = self.repo.cancel_active(12345)
        assert result is True

        sub = Subscription.objects.get(user_telegram_uid=12345)
        assert sub.status == SubscriptionStatus.CANCELLED

    def test_cancel_active_no_subscription(self):
        result = self.repo.cancel_active(99999)
        assert result is False

    def test_expire_overdue(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() - timedelta(days=1),
        )
        Subscription.objects.create(
            user_telegram_uid=67890,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )

        count = self.repo.expire_overdue()

        assert count == 1
        expired = Subscription.objects.get(user_telegram_uid=12345)
        assert expired.status == SubscriptionStatus.EXPIRED
        active = Subscription.objects.get(user_telegram_uid=67890)
        assert active.status == SubscriptionStatus.ACTIVE

    def test_get_expired_subscriptions(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() - timedelta(days=1),
        )

        result = self.repo.get_expired_subscriptions()

        assert len(result) == 1
        assert result[0].user_telegram_uid == 12345

    def test_get_expiring_soon(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=2),
            reminder_sent_at=None,
        )
        # Not expiring soon
        Subscription.objects.create(
            user_telegram_uid=67890,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
            reminder_sent_at=None,
        )

        result = self.repo.get_expiring_soon(days=3)

        assert len(result) == 1
        assert result[0].user_telegram_uid == 12345

    def test_get_expiring_soon_already_reminded(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=2),
            reminder_sent_at=timezone.now(),
        )

        result = self.repo.get_expiring_soon(days=3)
        assert len(result) == 0

    def test_get_recently_expired_unnotified(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.EXPIRED,
            expires_at=timezone.now() - timedelta(days=1),
            reminder_sent_at=None,
        )

        result = self.repo.get_recently_expired_unnotified()

        assert len(result) == 1
        assert result[0].user_telegram_uid == 12345

    def test_get_recently_expired_already_notified(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.EXPIRED,
            expires_at=timezone.now() - timedelta(days=1),
            reminder_sent_at=timezone.now(),
        )

        result = self.repo.get_recently_expired_unnotified()
        assert len(result) == 0

    def test_mark_reminded(self):
        sub = Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=2),
            reminder_sent_at=None,
        )

        count = self.repo.mark_reminded(subscription_ids=[sub.id])

        assert count == 1
        sub.refresh_from_db()
        assert sub.reminder_sent_at is not None
