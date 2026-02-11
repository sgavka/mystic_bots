import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from core.containers import container
from core.entities import UserEntity
from horoscope import callbacks
from horoscope.config import SUBSCRIPTION_DURATION_DAYS, SUBSCRIPTION_PRICE_STARS
from horoscope.services.subscription import SubscriptionService
from horoscope.translations import t

logger = logging.getLogger(__name__)

router = Router()


async def _aget_user_language(user: UserEntity) -> str:
    """Get user's preferred language from profile, fallback to 'en'."""
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    return profile.preferred_language if profile else 'en'


@router.callback_query(F.data == callbacks.SUBSCRIBE)
async def subscribe_callback(callback: CallbackQuery, user: UserEntity, **kwargs):
    await callback.answer()

    lang = await _aget_user_language(user)

    await callback.message.answer(
        t(
            "subscription.offer",
            lang,
            days=SUBSCRIPTION_DURATION_DAYS,
            price=SUBSCRIPTION_PRICE_STARS,
        ),
    )

    await callback.message.answer_invoice(
        title=t("subscription.invoice_title", lang),
        description=t("subscription.invoice_description", lang, days=SUBSCRIPTION_DURATION_DAYS),
        payload=f"subscription_{user.telegram_uid}",
        currency="XTR",
        prices=[LabeledPrice(label="Subscription", amount=SUBSCRIPTION_PRICE_STARS)],
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, **kwargs):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, user: UserEntity, **kwargs):
    payment = message.successful_payment
    service = SubscriptionService()

    subscription = await service.aactivate_subscription(
        telegram_uid=user.telegram_uid,
        duration_days=SUBSCRIPTION_DURATION_DAYS,
        payment_charge_id=payment.telegram_payment_charge_id,
    )

    logger.info(
        f"Subscription activated for user {user.telegram_uid} "
        f"until {subscription.expires_at}"
    )

    lang = await _aget_user_language(user)

    await message.answer(
        t(
            "subscription.payment_success",
            lang,
            expires=subscription.expires_at.strftime('%d.%m.%Y'),
        )
    )
