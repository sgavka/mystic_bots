import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='horoscope.generate_for_user',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def generate_horoscope_task(telegram_uid: int, target_date: str, horoscope_type: str = 'daily'):
    """
    Celery task to generate a horoscope for a specific user and date.

    Args:
        telegram_uid: User's Telegram UID
        target_date: ISO format date string (YYYY-MM-DD)
        horoscope_type: Type of horoscope ('daily' or 'first')
    """
    from horoscope.services.horoscope import HoroscopeService

    parsed_date = date.fromisoformat(target_date)
    service = HoroscopeService()

    try:
        horoscope = service.generate_for_user(
            telegram_uid=telegram_uid,
            target_date=parsed_date,
            horoscope_type=horoscope_type,
        )
        logger.info(
            f"Generated horoscope {horoscope.id} for user {telegram_uid} "
            f"on {target_date} (type={horoscope_type})"
        )
        return horoscope.id
    except ValueError as e:
        logger.error(f"Failed to generate horoscope for user {telegram_uid}: {e}")
        return None
