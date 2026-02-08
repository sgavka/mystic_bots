import logging
from datetime import timedelta
from typing import Optional

from asgiref.sync import sync_to_async
from django.utils import timezone

from core.containers import container
from horoscope.entities import SubscriptionEntity
from horoscope.enums import SubscriptionStatus
from horoscope.models import Subscription

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self):
        self.subscription_repo = container.horoscope.subscription_repository()

    def activate_subscription(
        self,
        telegram_uid: int,
        duration_days: int = 30,
        payment_charge_id: Optional[str] = None,
    ) -> SubscriptionEntity:
        try:
            sub = Subscription.objects.get(
                user_telegram_uid=telegram_uid,
                status=SubscriptionStatus.ACTIVE,
            )
            sub.expires_at = timezone.now() + timedelta(days=duration_days)
            if payment_charge_id:
                sub.telegram_payment_charge_id = payment_charge_id
            sub.save()
            return SubscriptionEntity.from_model(sub)
        except Subscription.DoesNotExist:
            sub = Subscription.objects.create(
                user_telegram_uid=telegram_uid,
                status=SubscriptionStatus.ACTIVE,
                expires_at=timezone.now() + timedelta(days=duration_days),
                telegram_payment_charge_id=payment_charge_id,
            )
            return SubscriptionEntity.from_model(sub)

    async def aactivate_subscription(
        self,
        telegram_uid: int,
        duration_days: int = 30,
        payment_charge_id: Optional[str] = None,
    ) -> SubscriptionEntity:
        return await sync_to_async(self.activate_subscription)(
            telegram_uid,
            duration_days,
            payment_charge_id,
        )

    def cancel_subscription(self, telegram_uid: int) -> bool:
        updated = Subscription.objects.filter(
            user_telegram_uid=telegram_uid,
            status=SubscriptionStatus.ACTIVE,
        ).update(status=SubscriptionStatus.CANCELLED)
        return updated > 0

    async def acancel_subscription(self, telegram_uid: int) -> bool:
        return await sync_to_async(self.cancel_subscription)(telegram_uid)

    def expire_overdue_subscriptions(self) -> int:
        count = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            expires_at__lte=timezone.now(),
        ).update(status=SubscriptionStatus.EXPIRED)
        if count > 0:
            logger.info(f"Expired {count} overdue subscriptions")
        return count

    async def aexpire_overdue_subscriptions(self) -> int:
        return await sync_to_async(self.expire_overdue_subscriptions)()

    def has_active_subscription(self, telegram_uid: int) -> bool:
        return self.subscription_repo.has_active_subscription(telegram_uid)

    async def ahas_active_subscription(self, telegram_uid: int) -> bool:
        return await sync_to_async(self.has_active_subscription)(telegram_uid)
