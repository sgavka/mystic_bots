import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='horoscope.generate_daily_for_all_users')
def generate_daily_for_all_users_task():
    """
    Celery beat task: generate daily horoscopes for all users with profiles.
    Runs once daily (configured in Celery beat schedule).
    """
    from horoscope.models import UserProfile
    from horoscope.tasks.generate_horoscope import generate_horoscope_task

    today = date.today()
    profiles = UserProfile.objects.all().values_list('user_telegram_uid', flat=True)

    count = 0
    for telegram_uid in profiles:
        generate_horoscope_task.delay(
            telegram_uid=telegram_uid,
            target_date=today.isoformat(),
            horoscope_type='daily',
        )
        count += 1

    logger.info(f"Queued daily horoscope generation for {count} users on {today}")
    return count


@shared_task(name='horoscope.send_daily_horoscope_notifications')
def send_daily_horoscope_notifications_task():
    """
    Celery beat task: send daily horoscope notifications to all users.
    Runs after generation is expected to be complete.
    """
    import asyncio
    from horoscope.models import UserProfile, Horoscope, Subscription
    from horoscope.enums import SubscriptionStatus

    today = date.today()
    profiles = UserProfile.objects.all()

    count = 0
    for profile in profiles:
        try:
            horoscope = Horoscope.objects.get(
                user_telegram_uid=profile.user_telegram_uid,
                date=today,
            )
        except Horoscope.DoesNotExist:
            logger.warning(f"No horoscope found for user {profile.user_telegram_uid} on {today}")
            continue

        has_subscription = Subscription.objects.filter(
            user_telegram_uid=profile.user_telegram_uid,
            status=SubscriptionStatus.ACTIVE,
        ).exists()

        if has_subscription:
            text = horoscope.full_text
        else:
            text = (
                horoscope.teaser_text
                + "\n\nSubscribe to see your full horoscope!"
            )

        _send_message_sync(
            telegram_uid=profile.user_telegram_uid,
            text=text,
        )
        count += 1

    logger.info(f"Sent daily horoscope to {count} users on {today}")
    return count


def _send_message_sync(telegram_uid: int, text: str):
    """Send a Telegram message synchronously (for Celery tasks)."""
    import asyncio
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from config import settings

    async def _send():
        bot = Bot(
            token=settings.CURRENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            await bot.send_message(chat_id=telegram_uid, text=text)
        except Exception as e:
            logger.error(f"Failed to send message to user {telegram_uid}: {e}")
        finally:
            await bot.session.close()

    asyncio.run(_send())
