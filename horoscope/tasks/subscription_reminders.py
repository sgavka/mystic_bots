import logging

from aiogram import Bot
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

TASK_EXPIRY_REMINDER = _(
    "⏰ Your horoscope subscription expires in <b>{days} day(s)</b>.\n"
    "\n"
    "Renew now to keep receiving your full daily horoscope! ✨\n"
    "\n"
    "Use /subscribe to renew."
)

TASK_SUBSCRIPTION_EXPIRED = _(
    "⚠️ Your horoscope subscription has <b>expired</b>.\n"
    "\n"
    "You'll now see a preview of your daily horoscope. Subscribe again to get full access! ⭐\n"
    "\n"
    "Use /subscribe to subscribe again."
)


async def send_expiry_reminders(bot: Bot) -> int:
    """
    Send reminders to users whose subscription is about to expire.
    """
    from django.conf import settings
    from django.utils import timezone

    from core.containers import container
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_messages_batch
    from horoscope.utils import translate

    subscription_repo = container.horoscope.subscription_repository()
    user_profile_repo = container.horoscope.user_profile_repository()

    expiring = await subscription_repo.aget_expiring_soon(days=settings.HOROSCOPE_SUBSCRIPTION_REMINDER_DAYS)

    if not expiring:
        return 0

    now = timezone.now()
    messages = []
    for sub in expiring:
        days_left = (sub.expires_at - now).days
        profile = await user_profile_repo.aget_by_telegram_uid(sub.user_telegram_uid)
        lang = profile.preferred_language if profile else 'en'
        text = translate(TASK_EXPIRY_REMINDER, lang, days=days_left)
        messages.append((sub.user_telegram_uid, text, subscribe_keyboard(language=lang)))

    count = await send_messages_batch(bot=bot, messages=messages)

    subscription_ids = [sub.id for sub in expiring]
    await subscription_repo.amark_reminded(subscription_ids=subscription_ids)

    logger.info(f"Sent expiry reminders to {count} users")
    return count


async def send_expired_notifications(bot: Bot) -> int:
    """
    Notify users whose subscription has just expired.
    Runs after expiring overdue subscriptions.
    """
    from core.containers import container
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_messages_batch
    from horoscope.utils import translate

    subscription_repo = container.horoscope.subscription_repository()
    user_profile_repo = container.horoscope.user_profile_repository()

    # First expire overdue subscriptions
    service = container.horoscope.subscription_service()
    await service.aexpire_overdue_subscriptions()

    expired = await subscription_repo.aget_recently_expired_unnotified()

    if not expired:
        return 0

    messages = []
    for sub in expired:
        profile = await user_profile_repo.aget_by_telegram_uid(sub.user_telegram_uid)
        lang = profile.preferred_language if profile else 'en'
        text = translate(TASK_SUBSCRIPTION_EXPIRED, lang)
        messages.append((sub.user_telegram_uid, text, subscribe_keyboard(language=lang)))

    count = await send_messages_batch(bot=bot, messages=messages)

    subscription_ids = [sub.id for sub in expired]
    await subscription_repo.amark_reminded(subscription_ids=subscription_ids)

    logger.info(f"Sent expired notifications to {count} users")
    return count
