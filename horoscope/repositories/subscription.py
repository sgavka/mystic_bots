from datetime import timedelta
from typing import Optional

from asgiref.sync import sync_to_async
from django.utils import timezone

from core.repositories.base import BaseRepository
from horoscope.entities import SubscriptionEntity
from horoscope.enums import SubscriptionStatus
from horoscope.exceptions import SubscriptionNotFoundException
from horoscope.models import Subscription


class SubscriptionRepository(BaseRepository[Subscription, SubscriptionEntity]):
    def __init__(self):
        super().__init__(
            model=Subscription,
            entity=SubscriptionEntity,
            not_found_exception=SubscriptionNotFoundException,
        )

    def get_active_by_user(self, telegram_uid: int) -> Optional[SubscriptionEntity]:
        try:
            sub = Subscription.objects.get(
                user_telegram_uid=telegram_uid,
                status=SubscriptionStatus.ACTIVE,
            )
            return SubscriptionEntity.from_model(sub)
        except Subscription.DoesNotExist:
            return None

    async def aget_active_by_user(self, telegram_uid: int) -> Optional[SubscriptionEntity]:
        return await sync_to_async(self.get_active_by_user)(telegram_uid)

    def has_active_subscription(self, telegram_uid: int) -> bool:
        return Subscription.objects.filter(
            user_telegram_uid=telegram_uid,
            status=SubscriptionStatus.ACTIVE,
        ).exists()

    async def ahas_active_subscription(self, telegram_uid: int) -> bool:
        return await sync_to_async(self.has_active_subscription)(telegram_uid)

    def get_expired_subscriptions(self) -> list[SubscriptionEntity]:
        subs = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            expires_at__lte=timezone.now(),
        )
        return [SubscriptionEntity.from_model(s) for s in subs]

    async def aget_expired_subscriptions(self) -> list[SubscriptionEntity]:
        return await sync_to_async(self.get_expired_subscriptions)()

    def activate_or_renew(
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
        except Subscription.DoesNotExist:
            sub = Subscription.objects.create(
                user_telegram_uid=telegram_uid,
                status=SubscriptionStatus.ACTIVE,
                expires_at=timezone.now() + timedelta(days=duration_days),
                telegram_payment_charge_id=payment_charge_id,
            )
        return SubscriptionEntity.from_model(sub)

    async def aactivate_or_renew(
        self,
        telegram_uid: int,
        duration_days: int = 30,
        payment_charge_id: Optional[str] = None,
    ) -> SubscriptionEntity:
        return await sync_to_async(self.activate_or_renew)(
            telegram_uid,
            duration_days,
            payment_charge_id,
        )

    def cancel_active(self, telegram_uid: int) -> bool:
        updated = Subscription.objects.filter(
            user_telegram_uid=telegram_uid,
            status=SubscriptionStatus.ACTIVE,
        ).update(status=SubscriptionStatus.CANCELLED)
        return updated > 0

    async def acancel_active(self, telegram_uid: int) -> bool:
        return await sync_to_async(self.cancel_active)(telegram_uid)

    def expire_overdue(self) -> int:
        return Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            expires_at__lte=timezone.now(),
        ).update(status=SubscriptionStatus.EXPIRED)

    async def aexpire_overdue(self) -> int:
        return await sync_to_async(self.expire_overdue)()
