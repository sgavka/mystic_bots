import logging
from datetime import date

from celery import shared_task
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

TASK_FIRST_HOROSCOPE_READY = _(
    "🔮 Your first horoscope is ready!\n"
    "\n"
    "{text}"
)


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
    from core.containers import container

    parsed_date = date.fromisoformat(target_date)
    service = container.horoscope.horoscope_service()

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

        if horoscope_type == 'first':
            _send_first_horoscope(
                telegram_uid=telegram_uid,
                horoscope_id=horoscope.id,
                full_text=horoscope.full_text,
            )
        else:
            _send_daily_horoscope(
                telegram_uid=telegram_uid,
                horoscope_id=horoscope.id,
                full_text=horoscope.full_text,
                teaser_text=horoscope.teaser_text,
            )

        return horoscope.id
    except ValueError as e:
        logger.error(f"Failed to generate horoscope for user {telegram_uid}: {e}")
        return None


def _send_daily_horoscope(
    telegram_uid: int,
    horoscope_id: int,
    full_text: str,
    teaser_text: str,
) -> None:
    """Send the daily horoscope: full text for subscribers, teaser with subscribe link for others."""
    from django.utils.translation import gettext_lazy as _

    from core.containers import container
    from horoscope.keyboards import subscribe_keyboard
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()
    user_profile_repo = container.horoscope.user_profile_repository()

    has_subscription = subscription_repo.has_active_subscription(telegram_uid=telegram_uid)
    profile = user_profile_repo.get_by_telegram_uid(telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    if has_subscription:
        text = full_text
        keyboard = None
    else:
        text = teaser_text + translate(_(
            "\n"
            "\n"
            "🔒 Subscribe to see your full daily horoscope!"
        ), lang)
        keyboard = subscribe_keyboard(language=lang)

    success = send_message(
        telegram_uid=telegram_uid,
        text=text,
        reply_markup=keyboard,
    )
    if success:
        horoscope_repo.mark_sent(horoscope_id=horoscope_id)
    else:
        horoscope_repo.mark_failed_to_send(horoscope_id=horoscope_id)
        logger.error(f"Failed to deliver daily horoscope to user {telegram_uid}")


def _send_first_horoscope(telegram_uid: int, horoscope_id: int, full_text: str) -> None:
    """Send the first horoscope to the user after profile setup."""
    from core.containers import container
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    profile = user_profile_repo.get_by_telegram_uid(telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    text = translate(TASK_FIRST_HOROSCOPE_READY, lang, text=full_text)
    success = send_message(telegram_uid=telegram_uid, text=text)
    if success:
        horoscope_repo.mark_sent(horoscope_id=horoscope_id)
    else:
        horoscope_repo.mark_failed_to_send(horoscope_id=horoscope_id)
        logger.error(f"Failed to deliver first horoscope to user {telegram_uid}")
