import asyncio
import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='horoscope.generate_daily_for_all_users',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def generate_daily_for_all_users_task():
    """
    Celery beat task: generate daily horoscopes for all users with profiles.
    Runs once daily (configured in Celery beat schedule).
    """
    from core.containers import container
    from horoscope.tasks.generate_horoscope import generate_horoscope_task

    today = date.today()
    user_profile_repo = container.horoscope.user_profile_repository()
    telegram_uids = user_profile_repo.get_all_telegram_uids()

    count = 0
    for telegram_uid in telegram_uids:
        generate_horoscope_task.delay(
            telegram_uid=telegram_uid,
            target_date=today.isoformat(),
            horoscope_type='daily',
        )
        count += 1

    logger.info(f"Queued daily horoscope generation for {count} users on {today}")
    return count


@shared_task(
    name='horoscope.send_daily_horoscope_notifications',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def send_daily_horoscope_notifications_task():
    """
    Celery beat task: send daily horoscope notifications to all users.
    Runs after generation is expected to be complete.
    """
    from core.containers import container
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.translations import t

    today = date.today()
    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()

    profiles = user_profile_repo.all()

    messages = []
    for profile in profiles:
        horoscope = horoscope_repo.get_by_user_and_date(
            telegram_uid=profile.user_telegram_uid,
            target_date=today,
        )
        if not horoscope:
            logger.warning(f"No horoscope found for user {profile.user_telegram_uid} on {today}")
            continue

        has_subscription = subscription_repo.has_active_subscription(
            telegram_uid=profile.user_telegram_uid,
        )

        lang = profile.preferred_language

        if has_subscription:
            text = horoscope.full_text
            keyboard = None
        else:
            text = horoscope.teaser_text + t("horoscope.subscribe_cta", lang)
            keyboard = subscribe_keyboard(language=lang)

        messages.append((profile.user_telegram_uid, text, keyboard))

    count = _send_messages_sync(messages)
    logger.info(f"Sent daily horoscope to {count} users on {today}")
    return count


def _send_messages_sync(messages: list[tuple[int, str, any]]) -> int:
    """Send multiple Telegram messages reusing a single Bot session."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from config import settings

    async def _send_all():
        bot = Bot(
            token=settings.CURRENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        sent = 0
        try:
            for telegram_uid, text, keyboard in messages:
                try:
                    await bot.send_message(
                        chat_id=telegram_uid,
                        text=text,
                        reply_markup=keyboard,
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send message to user {telegram_uid}: {e}")
        finally:
            await bot.session.close()
        return sent

    return asyncio.run(_send_all())
