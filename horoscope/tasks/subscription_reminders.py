import asyncio
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='horoscope.send_expiry_reminders',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def send_expiry_reminders_task():
    """
    Celery beat task: send reminders to users whose subscription is about to expire.
    """
    from core.containers import container
    from horoscope.config import SUBSCRIPTION_REMINDER_DAYS

    subscription_repo = container.horoscope.subscription_repository()
    expiring = subscription_repo.get_expiring_soon(days=SUBSCRIPTION_REMINDER_DAYS)

    if not expiring:
        return 0

    from django.utils import timezone

    messages = []
    now = timezone.now()
    for sub in expiring:
        days_left = (sub.expires_at - now).days
        text = (
            f"Your horoscope subscription expires in <b>{days_left} day(s)</b>.\n\n"
            "Renew now to keep receiving your full daily horoscope!"
        )
        messages.append((sub.user_telegram_uid, text))

    count = _send_messages_with_keyboard(messages)

    subscription_ids = [sub.id for sub in expiring]
    subscription_repo.mark_reminded(subscription_ids=subscription_ids)

    logger.info(f"Sent expiry reminders to {count} users")
    return count


@shared_task(
    name='horoscope.send_expired_notifications',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def send_expired_notifications_task():
    """
    Celery beat task: notify users whose subscription has just expired.
    Should run after expire_overdue_subscriptions.
    """
    from core.containers import container

    subscription_repo = container.horoscope.subscription_repository()

    # First expire overdue subscriptions
    from horoscope.services.subscription import SubscriptionService
    service = SubscriptionService()
    service.expire_overdue_subscriptions()

    expired = subscription_repo.get_recently_expired_unnotified()

    if not expired:
        return 0

    messages = []
    for sub in expired:
        text = (
            "Your horoscope subscription has <b>expired</b>.\n\n"
            "You'll now see a preview of your daily horoscope. "
            "Subscribe again to get full access!"
        )
        messages.append((sub.user_telegram_uid, text))

    count = _send_messages_with_keyboard(messages)

    subscription_ids = [sub.id for sub in expired]
    subscription_repo.mark_reminded(subscription_ids=subscription_ids)

    logger.info(f"Sent expired notifications to {count} users")
    return count


def _send_messages_with_keyboard(messages: list[tuple[int, str]]) -> int:
    """Send Telegram messages with subscribe keyboard, reusing a single Bot session."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from config import settings
    from horoscope.keyboards import subscribe_keyboard

    keyboard = subscribe_keyboard()

    async def _send_all():
        bot = Bot(
            token=settings.CURRENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        sent = 0
        try:
            for telegram_uid, text in messages:
                try:
                    await bot.send_message(
                        chat_id=telegram_uid,
                        text=text,
                        reply_markup=keyboard,
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send reminder to user {telegram_uid}: {e}")
        finally:
            await bot.session.close()
        return sent

    return asyncio.run(_send_all())
