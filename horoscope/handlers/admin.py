import logging
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from asgiref.sync import sync_to_async

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
):
    if user.telegram_uid not in settings.ADMIN_USERS_IDS:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await app_context.send_message(text="Usage: /refund <telegram_payment_charge_id>")
        return

    charge_id = args[1].strip()

    try:
        await app_context.bot.refund_star_payment(
            user_id=message.from_user.id,
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
        text=f"Refund successful for charge ID {charge_id}.",
    )


@router.message(Command("stats"))
async def stats_command_handler(
    message: Message,
    user: UserEntity,
    app_context: AppContext,
):
    if user.telegram_uid not in settings.ADMIN_USERS_IDS:
        return

    profile_repo = container.horoscope.user_profile_repository()
    subscription_repo = container.horoscope.subscription_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    followup_repo = container.horoscope.followup_repository()

    today = datetime.now().date()

    @sync_to_async
    def _gather_stats() -> dict:
        return {
            'total_profiles': profile_repo.count(),
            'total_subscriptions': subscription_repo.count(),
            'active_subscriptions': subscription_repo.count_active(),
            'total_horoscopes': horoscope_repo.count(),
            'total_followups': followup_repo.count(),
            'today_profiles': profile_repo.count_created_since(today),
            'today_subscriptions': subscription_repo.count_created_since(today),
            'today_horoscopes': horoscope_repo.count_created_since(today),
        }

    stats = await _gather_stats()

    text = (
        f"<b>Stats — {today.strftime('%d.%m.%Y')}</b>\n"
        f"\n"
        f"<b>Total:</b>\n"
        f"Users: {stats['total_profiles']}\n"
        f"Subscriptions: {stats['total_subscriptions']} (active: {stats['active_subscriptions']})\n"
        f"Horoscopes: {stats['total_horoscopes']}\n"
        f"Followup questions: {stats['total_followups']}\n"
        f"\n"
        f"<b>Today:</b>\n"
        f"New users: {stats['today_profiles']}\n"
        f"New subscriptions: {stats['today_subscriptions']}\n"
        f"Horoscopes generated: {stats['today_horoscopes']}"
    )

    await app_context.send_message(text=text)
