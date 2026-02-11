import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from core.entities import UserEntity
from horoscope import callbacks
from horoscope.config import SUBSCRIPTION_DURATION_DAYS, SUBSCRIPTION_PRICE_STARS
from horoscope.handlers.utils import aget_user_language
from horoscope.services.subscription import SubscriptionService
from horoscope.translations import t

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == callbacks.SUBSCRIBE)
async def subscribe_callback(callback: CallbackQuery, user: UserEntity, **kwargs):
    await callback.answer()

    lang = await aget_user_language(user)

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
    lang = await aget_user_language(user)

    try:
        subscription = await service.aactivate_subscription(
            telegram_uid=user.telegram_uid,
            duration_days=SUBSCRIPTION_DURATION_DAYS,
            payment_charge_id=payment.telegram_payment_charge_id,
        )
    except Exception:
        logger.exception(
            f"Failed to activate subscription for user {user.telegram_uid} "
            f"after payment {payment.telegram_payment_charge_id}"
        )
        await message.answer(t("error.payment_failed", lang))
        return

    logger.info(
        f"Subscription activated for user {user.telegram_uid} "
        f"until {subscription.expires_at}"
    )

    await message.answer(
        t(
            "subscription.payment_success",
            lang,
            expires=subscription.expires_at.strftime('%d.%m.%Y'),
        )
    )
