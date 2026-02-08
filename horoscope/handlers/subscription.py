import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from asgiref.sync import sync_to_async

from core.entities import UserEntity
from horoscope import callbacks
from horoscope.config import SUBSCRIPTION_DURATION_DAYS, SUBSCRIPTION_PRICE_STARS
from horoscope.services.subscription import SubscriptionService

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == callbacks.SUBSCRIBE)
async def subscribe_callback(callback: CallbackQuery, user: UserEntity, **kwargs):
    await callback.answer()

    await callback.message.answer(
        f"Subscribe for <b>{SUBSCRIPTION_DURATION_DAYS} days</b> "
        f"of full daily horoscope access.\n\n"
        f"Price: <b>{SUBSCRIPTION_PRICE_STARS} Telegram Stars</b>\n\n"
        "Tap the button below to pay.",
    )

    await callback.message.answer_invoice(
        title="Horoscope Subscription",
        description=f"{SUBSCRIPTION_DURATION_DAYS}-day access to full daily horoscope",
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

    @sync_to_async
    def _activate():
        return service.activate_subscription(
            telegram_uid=user.telegram_uid,
            duration_days=SUBSCRIPTION_DURATION_DAYS,
            payment_charge_id=payment.telegram_payment_charge_id,
        )

    subscription = await _activate()

    logger.info(
        f"Subscription activated for user {user.telegram_uid} "
        f"until {subscription.expires_at}"
    )

    await message.answer(
        "Payment successful! Your subscription is now active.\n\n"
        f"Expires: {subscription.expires_at.strftime('%B %d, %Y')}\n\n"
        "Use /horoscope to see your full daily horoscope."
    )
