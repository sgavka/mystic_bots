import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from config import settings
from django.utils.translation import gettext_lazy as _

from core.containers import container
from core.entities import UserEntity
from horoscope.callbacks import SubscribeCallback
from horoscope.handlers.utils import aget_user_language
from horoscope.utils import map_telegram_language, translate
from telegram_bot.app_context import AppContext

SUBSCRIPTION_OFFER = _(
    "⭐ Subscribe for <b>{days} days</b> of full daily horoscope access.\n"
    "\n"
    "💰 Price: <b>{price} Telegram Stars</b>\n"
    "\n"
    "Tap the button below to pay."
)

SUBSCRIPTION_ALREADY_ACTIVE = _(
    "✅ You already have an active subscription.\n"
    "\n"
    "📅 Expires: <b>{expires}</b>\n"
    "\n"
    "You can renew now — the new period will start from your current expiration date.\n"
    "\n"
    "💰 Price: <b>{price} Telegram Stars</b> for <b>{days} days</b>\n"
    "\n"
    "Tap the button below to extend."
)

SUBSCRIPTION_NO_PROFILE = _(
    "⚠️ You haven't set up your profile yet.\n"
    "Send /start to begin the onboarding wizard."
)

SUBSCRIPTION_INVOICE_TITLE = _("Horoscope Subscription")

SUBSCRIPTION_INVOICE_DESCRIPTION = _("{days}-day access to full daily horoscope")

SUBSCRIPTION_PAYMENT_SUCCESS = _(
    "✅ Payment successful! Your subscription is now active.\n"
    "\n"
    "📅 Expires: {expires}\n"
    "\n"
    "Use /horoscope to see your full daily horoscope ✨"
)

ERROR_PAYMENT_FAILED = _("😔 Something went wrong while activating your subscription. Please contact support if the issue persists.")

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("subscribe"))
async def subscribe_command(message: Message, user: UserEntity, app_context: AppContext, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    subscription_repo = container.horoscope.subscription_repository()

    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SUBSCRIPTION_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    active_sub = await subscription_repo.aget_active_by_user(user.telegram_uid)
    if active_sub:
        await app_context.send_message(
            text=translate(
                SUBSCRIPTION_ALREADY_ACTIVE,
                lang,
                expires=active_sub.expires_at.strftime('%d.%m.%Y'),
                price=settings.HOROSCOPE_SUBSCRIPTION_PRICE_STARS,
                days=settings.HOROSCOPE_SUBSCRIPTION_DURATION_DAYS,
            ),
        )
    else:
        await app_context.send_message(
            text=translate(
                SUBSCRIPTION_OFFER,
                lang,
                days=settings.HOROSCOPE_SUBSCRIPTION_DURATION_DAYS,
                price=settings.HOROSCOPE_SUBSCRIPTION_PRICE_STARS,
            ),
        )

    await app_context.send_invoice(
        title=translate(SUBSCRIPTION_INVOICE_TITLE, lang),
        description=translate(
            SUBSCRIPTION_INVOICE_DESCRIPTION,
            lang,
            days=settings.HOROSCOPE_SUBSCRIPTION_DURATION_DAYS,
        ),
        payload=f"subscription_{user.telegram_uid}",
        currency="XTR",
        prices=[LabeledPrice(
            label="Subscription",
            amount=settings.HOROSCOPE_SUBSCRIPTION_PRICE_STARS,
        )],
    )


@router.callback_query(SubscribeCallback.filter())
async def subscribe_callback(callback: CallbackQuery, user: UserEntity, app_context: AppContext, **kwargs):
    await callback.answer()

    lang = await aget_user_language(user)

    await app_context.send_message(
        text=translate(
            SUBSCRIPTION_OFFER,
            lang,
            days=settings.HOROSCOPE_SUBSCRIPTION_DURATION_DAYS,
            price=settings.HOROSCOPE_SUBSCRIPTION_PRICE_STARS,
        ),
    )

    await app_context.send_invoice(
        title=translate(SUBSCRIPTION_INVOICE_TITLE, lang),
        description=translate(SUBSCRIPTION_INVOICE_DESCRIPTION, lang, days=settings.HOROSCOPE_SUBSCRIPTION_DURATION_DAYS),
        payload=f"subscription_{user.telegram_uid}",
        currency="XTR",
        prices=[LabeledPrice(label="Subscription", amount=settings.HOROSCOPE_SUBSCRIPTION_PRICE_STARS)],
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, **kwargs):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, user: UserEntity, app_context: AppContext, **kwargs):
    payment = message.successful_payment
    service = container.horoscope.subscription_service()
    lang = await aget_user_language(user)

    try:
        subscription = await service.aactivate_subscription(
            telegram_uid=user.telegram_uid,
            duration_days=settings.HOROSCOPE_SUBSCRIPTION_DURATION_DAYS,
            payment_charge_id=payment.telegram_payment_charge_id,
        )
    except Exception:
        # Payment succeeded but DB activation failed — must not crash, user needs error feedback
        logger.exception(
            f"Failed to activate subscription for user {user.telegram_uid} "
            f"after payment {payment.telegram_payment_charge_id}"
        )
        await app_context.send_message(text=translate(ERROR_PAYMENT_FAILED, lang))
        return

    logger.info(
        f"Subscription activated for user {user.telegram_uid} "
        f"until {subscription.expires_at}"
    )

    await app_context.send_message(
        text=translate(
            SUBSCRIPTION_PAYMENT_SUCCESS,
            lang,
            expires=subscription.expires_at.strftime('%d.%m.%Y'),
        ),
    )
