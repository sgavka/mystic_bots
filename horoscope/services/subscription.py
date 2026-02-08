import logging
from typing import Optional

from asgiref.sync import sync_to_async

from core.containers import container
from horoscope.entities import SubscriptionEntity

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
        return self.subscription_repo.activate_or_renew(
            telegram_uid=telegram_uid,
            duration_days=duration_days,
            payment_charge_id=payment_charge_id,
        )

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
        return self.subscription_repo.cancel_active(telegram_uid=telegram_uid)

    async def acancel_subscription(self, telegram_uid: int) -> bool:
        return await sync_to_async(self.cancel_subscription)(telegram_uid)

    def expire_overdue_subscriptions(self) -> int:
        count = self.subscription_repo.expire_overdue()
        if count > 0:
            logger.info(f"Expired {count} overdue subscriptions")
        return count

    async def aexpire_overdue_subscriptions(self) -> int:
        return await sync_to_async(self.expire_overdue_subscriptions)()

    def has_active_subscription(self, telegram_uid: int) -> bool:
        return self.subscription_repo.has_active_subscription(telegram_uid)

    async def ahas_active_subscription(self, telegram_uid: int) -> bool:
        return await sync_to_async(self.has_active_subscription)(telegram_uid)
