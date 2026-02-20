import logging
from datetime import date

from aiogram import Bot
from django.utils.translation import gettext_lazy as _

from horoscope.enums import HoroscopeType

logger = logging.getLogger(__name__)

TASK_FIRST_HOROSCOPE_READY = _(
    "🔮 Your first horoscope is ready!\n"
    "\n"
    "{text}"
)


async def generate_horoscope(
    bot: Bot,
    telegram_uid: int,
    target_date: str,
    horoscope_type: HoroscopeType = HoroscopeType.DAILY,
) -> None:
    """
    Generate a horoscope for a specific user and date.

    For 'first' horoscope type, the horoscope is sent immediately after generation.
    For 'daily' type, generation only — separate notification tasks handle sending.

    Args:
        bot: The Bot instance for sending messages.
        telegram_uid: User's Telegram UID.
        target_date: ISO format date string (YYYY-MM-DD).
        horoscope_type: Type of horoscope ('daily' or 'first').
    """
    from core.containers import container

    parsed_date = date.fromisoformat(target_date)
    service = container.horoscope.horoscope_service()

    try:
        horoscope = await service.agenerate_for_user(
            telegram_uid=telegram_uid,
            target_date=parsed_date,
            horoscope_type=horoscope_type,
        )
        logger.info(
            f"Generated horoscope {horoscope.id} for user {telegram_uid} "
            f"on {target_date} (type={horoscope_type})"
        )

        if horoscope_type == HoroscopeType.FIRST:
            await _send_first_horoscope(
                bot=bot,
                telegram_uid=telegram_uid,
                horoscope_id=horoscope.id,
                full_text=horoscope.full_text,
            )
    except ValueError as e:
        logger.error(f"Failed to generate horoscope for user {telegram_uid}", exc_info=e)
        raise


async def generate_and_send_horoscope(
    bot: Bot,
    telegram_uid: int,
    target_date: str,
) -> None:
    """
    Generate a daily horoscope and send it immediately.

    Used for on-demand generation when a subscriber requests /horoscope
    but today's horoscope hasn't been generated yet.
    """
    from core.containers import container
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    await generate_horoscope(
        bot=bot,
        telegram_uid=telegram_uid,
        target_date=target_date,
        horoscope_type=HoroscopeType.DAILY,
    )

    horoscope_repo = container.horoscope.horoscope_repository()
    user_profile_repo = container.horoscope.user_profile_repository()

    parsed_date = date.fromisoformat(target_date)
    horoscope = await horoscope_repo.aget_by_user_and_date(
        telegram_uid=telegram_uid,
        target_date=parsed_date,
    )
    if not horoscope:
        logger.error(f"Horoscope not found after generation for user {telegram_uid} on {target_date}")
        return

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
    else:
        await horoscope_repo.amark_failed_to_send(horoscope_id=horoscope.id)
        logger.error(f"Failed to deliver on-demand horoscope to user {telegram_uid}")


async def _send_first_horoscope(
    bot: Bot,
    telegram_uid: int,
    horoscope_id: int,
    full_text: str,
) -> None:
    """Send the first horoscope to the user after profile setup."""
    from django.utils.translation import gettext_lazy as _

    from core.containers import container
    from horoscope.tasks.messaging import send_message
    from horoscope.utils import translate

    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    has_subscription = await subscription_repo.ahas_active_subscription(telegram_uid=telegram_uid)
    followup_hint = ""
    if has_subscription:
        followup_hint = translate(_(
            "\n"
            "\n"
            "💬 You can ask questions about your horoscope — just type your message!"
        ), lang)

    text = translate(TASK_FIRST_HOROSCOPE_READY, lang, text=full_text + followup_hint)
    success = await send_message(
        bot=bot,
        telegram_uid=telegram_uid,
        text=text,
    )
    if success:
        await horoscope_repo.amark_sent(horoscope_id=horoscope_id)
    else:
        await horoscope_repo.amark_failed_to_send(horoscope_id=horoscope_id)
        logger.error(f"Failed to deliver first horoscope to user {telegram_uid}")
