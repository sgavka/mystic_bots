import logging
from datetime import date

from aiogram import Bot

logger = logging.getLogger(__name__)


async def generate_daily_for_all_users(bot: Bot) -> int:
    """
    Generate daily horoscopes for users whose notification hour matches the current UTC hour.
    - Subscribers: always generate
    - Non-subscribers: only generate if active within HOROSCOPE_ACTIVITY_WINDOW_DAYS
    """
    from datetime import timedelta

    from django.conf import settings
    from django.utils import timezone

    from core.containers import container
    from horoscope.enums import HoroscopeType
    from horoscope.tasks.generate_horoscope import generate_horoscope

    today = date.today()
    current_utc_hour = timezone.now().hour
    user_profile_repo = container.horoscope.user_profile_repository()
    subscription_repo = container.horoscope.subscription_repository()
    user_repo = container.core.user_repository()

    telegram_uids = await user_profile_repo.aget_telegram_uids_by_notification_hour(
        hour_utc=current_utc_hour,
    )

    activity_cutoff = timezone.now() - timedelta(days=settings.HOROSCOPE_ACTIVITY_WINDOW_DAYS)

    count = 0
    for telegram_uid in telegram_uids:
        has_subscription = await subscription_repo.ahas_active_subscription(telegram_uid=telegram_uid)

        if not has_subscription:
            user = await user_repo.aget(telegram_uid)
            if not user:
                continue
            if not user.last_activity or user.last_activity < activity_cutoff:
                continue

        try:
            await generate_horoscope(
                bot=bot,
                telegram_uid=telegram_uid,
                target_date=today.isoformat(),
                horoscope_type=HoroscopeType.DAILY,
            )
            count += 1
        except Exception as e:
            # Individual user failure must not stop generation for other users
            logger.error(f"Failed to generate daily horoscope for user {telegram_uid}", exc_info=e)

    logger.info(f"Generated daily horoscopes for {count} users on {today} (UTC hour={current_utc_hour})")
    return count


async def send_daily_horoscope_notifications(bot: Bot) -> int:
    """
    Send daily horoscope notifications to subscribers who have generated but unsent horoscopes.
    Queries all unsent horoscopes for today regardless of current hour to avoid race conditions
    between generation and sending tasks.
    """
    from django.utils.translation import gettext_lazy as _

    from core.containers import container
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    today = date.today()
    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()

    telegram_uids = await horoscope_repo.aget_unsent_telegram_uids_for_date(
        target_date=today,
    )

    count = 0
    for telegram_uid in telegram_uids:
        has_subscription = await subscription_repo.ahas_active_subscription(
            telegram_uid=telegram_uid,
        )
        if not has_subscription:
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

        text = horoscope.full_text + translate(_(
            "\n"
            "\n"
            "💬 You can ask questions about your horoscope — just type your message!"
        ), lang)

        success = await send_message(
            bot=bot,
            telegram_uid=telegram_uid,
            text=text,
        )
        if success:
            await horoscope_repo.amark_sent(horoscope_id=horoscope.id)
            count += 1
        else:
            await horoscope_repo.amark_failed_to_send(horoscope_id=horoscope.id)

    logger.info(f"Sent daily horoscope to {count} subscribers on {today}")
    return count
