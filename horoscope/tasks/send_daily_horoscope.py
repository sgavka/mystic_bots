import logging
from datetime import date

from aiogram import Bot

logger = logging.getLogger(__name__)


async def generate_daily_for_all_users(bot: Bot) -> int:
    """
    Generate daily horoscopes for users with profiles.
    - Subscribers: always generate
    - Non-subscribers: only generate if active within HOROSCOPE_ACTIVITY_WINDOW_DAYS
    """
    from datetime import timedelta

    from django.conf import settings
    from django.utils import timezone

    from core.containers import container
    from horoscope.tasks.generate_horoscope import generate_horoscope

    today = date.today()
    user_profile_repo = container.horoscope.user_profile_repository()
    subscription_repo = container.horoscope.subscription_repository()
    user_repo = container.core.user_repository()
    telegram_uids = await user_profile_repo.aget_all_telegram_uids()

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
                horoscope_type='daily',
                send_after_generation=False,
            )
            count += 1
        except Exception as e:
            # Individual user failure must not stop generation for other users
            logger.error(f"Failed to generate daily horoscope for user {telegram_uid}", exc_info=e)

    logger.info(f"Generated daily horoscopes for {count} users on {today}")
    return count


async def send_daily_horoscope_notifications(bot: Bot) -> int:
    """
    Send daily horoscope notifications to subscribers only.
    Non-subscribers receive periodic teasers via a separate task.
    """
    from django.utils.translation import gettext_lazy as _

    from core.containers import container
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    today = date.today()
    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()

    profiles = await user_profile_repo.aall()

    count = 0
    for profile in profiles:
        has_subscription = await subscription_repo.ahas_active_subscription(
            telegram_uid=profile.user_telegram_uid,
        )
        if not has_subscription:
            continue

        horoscope = await horoscope_repo.aget_by_user_and_date(
            telegram_uid=profile.user_telegram_uid,
            target_date=today,
        )
        if not horoscope:
            logger.warning(f"No horoscope found for user {profile.user_telegram_uid} on {today}")
            continue

        if horoscope.sent_at is not None:
            continue

        lang = profile.preferred_language
        text = horoscope.full_text + translate(_(
            "\n"
            "\n"
            "💬 You can ask questions about your horoscope — just type your message!"
        ), lang)

        success = await send_message(
            bot=bot,
            telegram_uid=profile.user_telegram_uid,
            text=text,
        )
        if success:
            await horoscope_repo.amark_sent(horoscope_id=horoscope.id)
            count += 1
        else:
            await horoscope_repo.amark_failed_to_send(horoscope_id=horoscope.id)

    logger.info(f"Sent daily horoscope to {count} subscribers on {today}")
    return count
