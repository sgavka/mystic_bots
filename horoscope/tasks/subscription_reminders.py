import logging

from celery import shared_task
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

TASK_EXPIRY_REMINDER = _(
    "⏰ Your horoscope subscription expires in <b>{days} day(s)</b>.\n"
    "\n"
    "Renew now to keep receiving your full daily horoscope! ✨"
)

TASK_SUBSCRIPTION_EXPIRED = _(
    "⚠️ Your horoscope subscription has <b>expired</b>.\n"
    "\n"
    "You'll now see a preview of your daily horoscope. Subscribe again to get full access! ⭐"
)


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
    from django.conf import settings
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_messages_batch
    from horoscope.utils import translate

    subscription_repo = container.horoscope.subscription_repository()
    user_profile_repo = container.horoscope.user_profile_repository()

    expiring = subscription_repo.get_expiring_soon(days=settings.HOROSCOPE_SUBSCRIPTION_REMINDER_DAYS)

    if not expiring:
        return 0

    from django.utils import timezone

    messages = []
    now = timezone.now()
    for sub in expiring:
        days_left = (sub.expires_at - now).days
        profile = user_profile_repo.get_by_telegram_uid(sub.user_telegram_uid)
        lang = profile.preferred_language if profile else 'en'
        text = translate(TASK_EXPIRY_REMINDER, lang, days=days_left)
        messages.append((sub.user_telegram_uid, text, subscribe_keyboard(language=lang)))

    count = send_messages_batch(messages)

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
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_messages_batch
    from horoscope.utils import translate

    subscription_repo = container.horoscope.subscription_repository()
    user_profile_repo = container.horoscope.user_profile_repository()

    # First expire overdue subscriptions
    service = container.horoscope.subscription_service()
    service.expire_overdue_subscriptions()

    expired = subscription_repo.get_recently_expired_unnotified()

    if not expired:
        return 0

    messages = []
    for sub in expired:
        profile = user_profile_repo.get_by_telegram_uid(sub.user_telegram_uid)
        lang = profile.preferred_language if profile else 'en'
        text = translate(TASK_SUBSCRIPTION_EXPIRED, lang)
        messages.append((sub.user_telegram_uid, text, subscribe_keyboard(language=lang)))

    count = send_messages_batch(messages)

    subscription_ids = [sub.id for sub in expired]
    subscription_repo.mark_reminded(subscription_ids=subscription_ids)

    logger.info(f"Sent expired notifications to {count} users")
    return count
