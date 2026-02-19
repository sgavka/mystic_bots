import logging
from datetime import date

from aiogram import Bot

logger = logging.getLogger(__name__)


async def send_periodic_teaser_notifications(bot: Bot) -> int:
    """
    Send periodic extended teaser horoscopes to non-subscribers whose notification
    hour matches the current UTC hour.
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
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    today = date.today()
    now = timezone.now()
    current_utc_hour = now.hour
    activity_cutoff = now - timedelta(days=settings.HOROSCOPE_ACTIVITY_WINDOW_DAYS)
    interval_cutoff = now - timedelta(days=settings.HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS)

    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()
    user_repo = container.core.user_repository()

    telegram_uids = await user_profile_repo.aget_telegram_uids_by_notification_hour(
        hour_utc=current_utc_hour,
    )

    count = 0
    for telegram_uid in telegram_uids:
        has_subscription = await subscription_repo.ahas_active_subscription(
            telegram_uid=telegram_uid,
        )
        if has_subscription:
            continue

        user = await user_repo.aget(telegram_uid)
        if not user:
            continue

        if not user.last_activity or user.last_activity < activity_cutoff:
            continue

        last_sent = await horoscope_repo.aget_last_sent_at(telegram_uid=telegram_uid)
        if last_sent and last_sent >= interval_cutoff:
            continue

        horoscope = await horoscope_repo.aget_by_user_and_date(
            telegram_uid=telegram_uid,
            target_date=today,
        )
        if not horoscope:
            continue

        if horoscope.sent_at is not None:
            continue

        profile = await user_profile_repo.aget_by_telegram_uid(telegram_uid)
        lang = profile.preferred_language if profile else 'en'

        text = horoscope.extended_teaser_text + translate(_(
            "\n"
            "\n"
            "🔒 Subscribe to see your full daily horoscope!"
        ), lang)
        keyboard = subscribe_keyboard(language=lang)

        success = await send_message(
            bot=bot,
            telegram_uid=telegram_uid,
            text=text,
            reply_markup=keyboard,
        )
        if success:
            await horoscope_repo.amark_sent(horoscope_id=horoscope.id)
            count += 1
        else:
            await horoscope_repo.amark_failed_to_send(horoscope_id=horoscope.id)

    logger.info(f"Sent periodic teaser horoscope to {count} non-subscribers on {today} (UTC hour={current_utc_hour})")
    return count
