import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from django.conf import settings

from core.containers import container
from core.entities import UserEntity
from telegram_bot.app_context import AppContext

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("refund"))
async def refund_command_handler(
    message: Message,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    if user.telegram_uid not in settings.ADMIN_USERS_IDS:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await app_context.send_message(text="Usage: /refund <telegram_payment_charge_id>")
        return

    charge_id = args[1].strip()

    subscription_repo = container.horoscope.subscription_repository()
    subscription = await subscription_repo.aget_by_charge_id(charge_id)

    if not subscription:
        await app_context.send_message(
            text=f"Subscription with charge ID {charge_id} not found.",
        )
        return

    try:
        await app_context.bot.refund_star_payment(
            user_id=subscription.user_telegram_uid,
            telegram_payment_charge_id=charge_id,
        )
    except Exception as e:
        # Telegram API refund can fail for various reasons — report to admin
        logger.error("Failed to refund payment", exc_info=e)
        await app_context.send_message(
            text=f"Refund failed: {e}",
        )
        return

    await app_context.send_message(
        text=f"Refund successful for charge ID {charge_id} (user {subscription.user_telegram_uid}).",
    )
