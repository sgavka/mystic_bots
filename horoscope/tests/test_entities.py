from datetime import date, timedelta

import pytest
from django.utils import timezone

from horoscope.entities import HoroscopeEntity, SubscriptionEntity, UserProfileEntity
from horoscope.enums import HoroscopeType, SubscriptionStatus
from horoscope.models import Horoscope, Subscription, UserProfile


@pytest.mark.django_db
class TestUserProfileEntity:
    def test_from_model(self):
        model = UserProfile.objects.create(
            user_telegram_uid=12345,
            name="Test User",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
        )

        entity = UserProfileEntity.from_model(model)

        assert entity.user_telegram_uid == 12345
        assert entity.name == "Test User"
        assert entity.date_of_birth == date(1990, 5, 15)
        assert entity.place_of_birth == "London"
        assert entity.place_of_living == "Berlin"
        assert entity.preferred_language == "en"
        assert entity.created_at is not None
        assert entity.updated_at is not None


@pytest.mark.django_db
class TestHoroscopeEntity:
    def test_from_model(self):
        model = Horoscope.objects.create(
            user_telegram_uid=12345,
            horoscope_type=HoroscopeType.DAILY,
            date=date(2024, 6, 15),
            full_text="Full horoscope text",
            teaser_text="Teaser text",
        )

        entity = HoroscopeEntity.from_model(model)

        assert entity.id == model.id
        assert entity.user_telegram_uid == 12345
        assert entity.horoscope_type == HoroscopeType.DAILY
        assert entity.date == date(2024, 6, 15)
        assert entity.full_text == "Full horoscope text"
        assert entity.teaser_text == "Teaser text"
        assert entity.created_at is not None


@pytest.mark.django_db
class TestSubscriptionEntity:
    def test_from_model(self):
        now = timezone.now()
        model = Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=now + timedelta(days=30),
            telegram_payment_charge_id="charge_123",
        )

        entity = SubscriptionEntity.from_model(model)

        assert entity.id == model.id
        assert entity.user_telegram_uid == 12345
        assert entity.status == SubscriptionStatus.ACTIVE
        assert entity.expires_at is not None
        assert entity.telegram_payment_charge_id == "charge_123"
        assert entity.created_at is not None
        assert entity.updated_at is not None

    def test_is_active_property(self):
        now = timezone.now()
        model = Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=now + timedelta(days=30),
        )

        entity = SubscriptionEntity.from_model(model)
        assert entity.is_active is True

    def test_is_active_false_when_expired(self):
        now = timezone.now()
        model = Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.EXPIRED,
            expires_at=now - timedelta(days=1),
        )

        entity = SubscriptionEntity.from_model(model)
        assert entity.is_active is False
