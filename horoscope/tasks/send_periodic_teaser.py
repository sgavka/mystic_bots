import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='horoscope.send_periodic_teaser_notifications',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def send_periodic_teaser_notifications_task():
    """
    Celery beat task: send periodic extended teaser horoscopes to non-subscribers.
    Only sends to users who:
    - Do NOT have an active subscription
    - Have been active within HOROSCOPE_ACTIVITY_WINDOW_DAYS
    - Have not received a periodic teaser in the last HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS
    """
    from datetime import timedelta

    from django.conf import settings
    from django.utils import timezone
    from django.utils.translation import gettext_lazy as _

    from core.containers import container
    from core.models import User
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    today = date.today()
    now = timezone.now()
    activity_cutoff = now - timedelta(days=settings.HOROSCOPE_ACTIVITY_WINDOW_DAYS)
    interval_cutoff = now - timedelta(days=settings.HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS)

    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()

    profiles = user_profile_repo.all()

    count = 0
    for profile in profiles:
        has_subscription = subscription_repo.has_active_subscription(
            telegram_uid=profile.user_telegram_uid,
        )
        if has_subscription:
            continue

        try:
            user = User.objects.get(telegram_uid=profile.user_telegram_uid)
        except User.DoesNotExist:
            continue

        if not user.last_activity or user.last_activity < activity_cutoff:
            continue

        last_sent = horoscope_repo.get_last_sent_at(telegram_uid=profile.user_telegram_uid)
        if last_sent and last_sent >= interval_cutoff:
            continue

        horoscope = horoscope_repo.get_by_user_and_date(
            telegram_uid=profile.user_telegram_uid,
            target_date=today,
        )
        if not horoscope:
            logger.warning(f"No horoscope found for user {profile.user_telegram_uid} on {today}")
            continue

        lang = profile.preferred_language
        text = horoscope.extended_teaser_text + translate(_(
            "\n"
            "\n"
            "🔒 Subscribe to see your full daily horoscope!"
        ), lang)
        keyboard = subscribe_keyboard(language=lang)

        success = send_message(
            telegram_uid=profile.user_telegram_uid,
            text=text,
            reply_markup=keyboard,
        )
        if success:
            horoscope_repo.mark_sent(horoscope_id=horoscope.id)
            count += 1
        else:
            horoscope_repo.mark_failed_to_send(horoscope_id=horoscope.id)

    logger.info(f"Sent periodic teaser horoscope to {count} non-subscribers on {today}")
    return count
