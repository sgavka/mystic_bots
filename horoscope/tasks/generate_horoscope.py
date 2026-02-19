import logging
from datetime import date

from aiogram import Bot
from django.utils.translation import gettext_lazy as _

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
    horoscope_type: str = 'daily',
    send_after_generation: bool = True,
) -> None:
    """
    Generate a horoscope for a specific user and date, optionally sending it.

    Args:
        bot: The Bot instance for sending messages.
        telegram_uid: User's Telegram UID.
        target_date: ISO format date string (YYYY-MM-DD).
        horoscope_type: Type of horoscope ('daily' or 'first').
        send_after_generation: If True, send the horoscope immediately after generation.
            Set to False when generation is part of a batch job where separate
            notification tasks handle sending.
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

        if send_after_generation:
            if horoscope_type == 'first':
                await _send_first_horoscope(
                    bot=bot,
                    telegram_uid=telegram_uid,
                    horoscope_id=horoscope.id,
                    full_text=horoscope.full_text,
                )
            else:
                await _send_daily_horoscope(
                    bot=bot,
                    telegram_uid=telegram_uid,
                    horoscope_id=horoscope.id,
                    full_text=horoscope.full_text,
                    teaser_text=horoscope.teaser_text,
                    extended_teaser_text=horoscope.extended_teaser_text,
                )
    except ValueError as e:
        logger.error(f"Failed to generate horoscope for user {telegram_uid}", exc_info=e)
        raise


async def _send_daily_horoscope(
    bot: Bot,
    telegram_uid: int,
    horoscope_id: int,
    full_text: str,
    teaser_text: str,
    extended_teaser_text: str = '',
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

    has_subscription = await subscription_repo.ahas_active_subscription(telegram_uid=telegram_uid)
    profile = await user_profile_repo.aget_by_telegram_uid(telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    if has_subscription:
        text = full_text + translate(_(
            "\n"
            "\n"
            "💬 You can ask questions about your horoscope — just type your message!"
        ), lang)
        keyboard = None
    else:
        text = teaser_text + translate(_(
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
        await horoscope_repo.amark_sent(horoscope_id=horoscope_id)
    else:
        await horoscope_repo.amark_failed_to_send(horoscope_id=horoscope_id)
        logger.error(f"Failed to deliver daily horoscope to user {telegram_uid}")


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
