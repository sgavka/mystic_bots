from datetime import timedelta

import pytest
from django.utils import timezone

from horoscope.enums import SubscriptionStatus
from horoscope.models import Subscription
from horoscope.services.subscription import SubscriptionService


@pytest.mark.django_db
class TestSubscriptionService:
    def setup_method(self):
        self.service = SubscriptionService()

    def test_activate_new_subscription(self):
        sub = self.service.activate_subscription(
            telegram_uid=12345,
            duration_days=30,
        )

        assert sub.user_telegram_uid == 12345
        assert sub.status == SubscriptionStatus.ACTIVE
        assert sub.expires_at is not None

    def test_activate_renewal(self):
        # Create initial subscription
        self.service.activate_subscription(
            telegram_uid=12345,
            duration_days=10,
        )

        # Renew
        sub = self.service.activate_subscription(
            telegram_uid=12345,
            duration_days=30,
        )

        assert sub.user_telegram_uid == 12345
        assert sub.status == SubscriptionStatus.ACTIVE
        # Should only be one active subscription
        assert Subscription.objects.filter(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
        ).count() == 1

    def test_activate_with_payment_charge_id(self):
        sub = self.service.activate_subscription(
            telegram_uid=12345,
            duration_days=30,
            payment_charge_id="charge_123",
        )

        assert sub.telegram_payment_charge_id == "charge_123"

    def test_cancel_subscription(self):
        self.service.activate_subscription(
            telegram_uid=12345,
            duration_days=30,
        )

        result = self.service.cancel_subscription(telegram_uid=12345)

        assert result is True
        assert not self.service.has_active_subscription(telegram_uid=12345)

    def test_cancel_nonexistent_subscription(self):
        result = self.service.cancel_subscription(telegram_uid=99999)

        assert result is False

    def test_expire_overdue_subscriptions(self):
        # Create expired subscription
        sub = Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() - timedelta(days=1),
        )

        count = self.service.expire_overdue_subscriptions()

        assert count == 1
        sub.refresh_from_db()
        assert sub.status == SubscriptionStatus.EXPIRED

    def test_expire_overdue_skips_future(self):
        Subscription.objects.create(
            user_telegram_uid=12345,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=10),
        )

        count = self.service.expire_overdue_subscriptions()

        assert count == 0

    def test_has_active_subscription(self):
        assert not self.service.has_active_subscription(telegram_uid=12345)

        self.service.activate_subscription(
            telegram_uid=12345,
            duration_days=30,
        )

        assert self.service.has_active_subscription(telegram_uid=12345)
