"""
Tests for horoscope repositories.
Covers UserProfileRepository, HoroscopeRepository, LLMUsageRepository, SubscriptionRepository.
"""

from datetime import date, timedelta

import pytest
from django.utils import timezone

from horoscope.entities import HoroscopeEntity, LLMUsageEntity, SubscriptionEntity, UserProfileEntity
from horoscope.enums import HoroscopeType, SubscriptionStatus
from horoscope.models import Horoscope, LLMUsage, Subscription, UserProfile
from horoscope.repositories.horoscope import HoroscopeRepository
from horoscope.repositories.llm_usage import LLMUsageRepository
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
            horoscope_type=HoroscopeType.DAILY,
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
            horoscope_type=HoroscopeType.DAILY,
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
            horoscope_type=HoroscopeType.DAILY,
            target_date=date(2024, 6, 15),
            full_text="Generated horoscope",
            teaser_text="Preview...",
        )

        assert isinstance(result, HoroscopeEntity)
        assert result.full_text == "Generated horoscope"
        assert result.teaser_text == "Preview..."
        assert Horoscope.objects.filter(user_telegram_uid=12345).exists()

    def test_mark_sent(self):
        horoscope = Horoscope.objects.create(
            user_telegram_uid=12345,
            horoscope_type=HoroscopeType.DAILY,
            date=date(2024, 6, 15),
            full_text="Full text",
            teaser_text="Teaser",
        )
        assert horoscope.sent_at is None

        self.repo.mark_sent(horoscope_id=horoscope.id)

        horoscope.refresh_from_db()
        assert horoscope.sent_at is not None

    def test_mark_failed_to_send(self):
        horoscope = Horoscope.objects.create(
            user_telegram_uid=12345,
            horoscope_type=HoroscopeType.DAILY,
            date=date(2024, 6, 15),
            full_text="Full text",
            teaser_text="Teaser",
        )
        assert horoscope.failed_to_send_at is None

        self.repo.mark_failed_to_send(horoscope_id=horoscope.id)

        horoscope.refresh_from_db()
        assert horoscope.failed_to_send_at is not None


@pytest.mark.django_db
class TestLLMUsageRepository:
    def setup_method(self):
        self.repo = LLMUsageRepository()
        self.profile = UserProfile.objects.create(
            user_telegram_uid=12345,
            name="Alice",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
        )

    def _create_horoscope(self, target_date=None):
        return Horoscope.objects.create(
            user_telegram_uid=12345,
            horoscope_type=HoroscopeType.DAILY,
            date=target_date or date(2024, 6, 15),
            full_text="Full text",
            teaser_text="Teaser...",
        )

    def test_create_usage(self):
        horoscope = self._create_horoscope()
        result = self.repo.create_usage(
            horoscope_id=horoscope.id,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
        )

        assert isinstance(result, LLMUsageEntity)
        assert result.horoscope_id == horoscope.id
        assert result.model == "gpt-4o-mini"
        assert result.input_tokens == 100
        assert result.output_tokens == 200

    def test_get_by_horoscope_id_found(self):
        horoscope = self._create_horoscope()
        LLMUsage.objects.create(
            horoscope=horoscope,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
        )

        result = self.repo.get_by_horoscope_id(horoscope.id)

        assert result is not None
        assert isinstance(result, LLMUsageEntity)
        assert result.model == "gpt-4o-mini"

    def test_get_by_horoscope_id_not_found(self):
        result = self.repo.get_by_horoscope_id(99999)
        assert result is None

    def test_get_usage_summary(self):
        h1 = self._create_horoscope(target_date=date(2024, 6, 15))
        h2 = self._create_horoscope(target_date=date(2024, 6, 16))
        h3 = self._create_horoscope(target_date=date(2024, 6, 17))

        LLMUsage.objects.create(horoscope=h1, model="gpt-4o-mini", input_tokens=100, output_tokens=200)
        LLMUsage.objects.create(horoscope=h2, model="gpt-4o-mini", input_tokens=150, output_tokens=250)
        LLMUsage.objects.create(horoscope=h3, model="gpt-4", input_tokens=300, output_tokens=400)

        summary = self.repo.get_usage_summary()

        assert len(summary) == 2
        mini_row = next(r for r in summary if r['model'] == 'gpt-4o-mini')
        assert mini_row['total_input_tokens'] == 250
        assert mini_row['total_output_tokens'] == 450

        gpt4_row = next(r for r in summary if r['model'] == 'gpt-4')
        assert gpt4_row['total_input_tokens'] == 300
        assert gpt4_row['total_output_tokens'] == 400

    def test_get_usage_summary_empty(self):
        summary = self.repo.get_usage_summary()
        assert summary == []


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

    def test_activate_or_renew_extends_from_expiration_date(self):
        """When renewing, new expiration should extend from current expiration date, not from now."""
        future_expiration = timezone.now() + timedelta(days=10)
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=future_expiration,
        )

        result = self.repo.activate_or_renew(
            telegram_uid=12345,
            duration_days=30,
        )

        assert result is not None
        sub = Subscription.objects.get(user_telegram_uid=12345)
        # Should extend from the expiration date (10 days from now + 30 days)
        expected_min = future_expiration + timedelta(days=29)
        expected_max = future_expiration + timedelta(days=31)
        assert expected_min <= sub.expires_at <= expected_max

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
