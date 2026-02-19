import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from django.utils.translation import gettext_lazy as _

from core.containers import container
from core.entities import UserEntity
from horoscope.callbacks import (
    NotificationHourCallback,
    ResetNotificationHourCallback,
    TimezoneCallback,
)
from horoscope.keyboards import notification_hour_keyboard, timezone_keyboard
from horoscope.utils import map_telegram_language, translate
from telegram_bot.app_context import AppContext

logger = logging.getLogger(__name__)

router = Router()

SETTINGS_NO_PROFILE = _(
    "⚠️ You haven't set up your profile yet.\n"
    "Send /start to begin."
)

TIMEZONE_CURRENT = _(
    "🕐 Your current timezone: <b>{timezone}</b>\n"
    "\n"
    "Choose your UTC offset:"
)

TIMEZONE_NOT_SET = _(
    "🕐 Your timezone is not set yet.\n"
    "\n"
    "Choose your UTC offset:"
)

TIMEZONE_CHANGED = _("✅ Timezone changed to <b>{timezone}</b>")

NOTIFICATION_TIME_CURRENT = _(
    "🔔 Your notification time: <b>{time}</b> (local time)\n"
    "\n"
    "Choose when you want to receive your daily horoscope:"
)

NOTIFICATION_TIME_DEFAULT = _(
    "🔔 You're using the default notification time for your language.\n"
    "\n"
    "Choose when you want to receive your daily horoscope:"
)

NOTIFICATION_TIME_CHANGED = _("✅ Notification time changed to <b>{time}</b> (local time)")

NOTIFICATION_TIME_RESET = _("✅ Notification time reset to language default.")

NOTIFICATION_TIME_SET_TIMEZONE_FIRST = _(
    "⚠️ Please set your timezone first with /timezone\n"
    "so we can show you the correct local time."
)


def _format_utc_offset(offset: int) -> str:
    """Format UTC offset integer to display string like UTC+3 or UTC-5."""
    if offset >= 0:
        return f"UTC+{offset}"
    return f"UTC{offset}"


def _parse_timezone_offset(timezone_str: str) -> int:
    """Parse UTC offset from timezone string like 'UTC+3' or 'UTC-5'. Returns 0 if invalid."""
    if not timezone_str or not timezone_str.startswith("UTC"):
        return 0
    try:
        offset_str = timezone_str[3:]
        if offset_str.startswith('+'):
            return int(offset_str[1:])
        elif offset_str.startswith('-'):
            return -int(offset_str[1:])
        return 0
    except (ValueError, IndexError):
        return 0


def _local_hour_to_utc(local_hour: int, utc_offset: int) -> int:
    """Convert a local hour (0-23) to UTC hour using the UTC offset."""
    return (local_hour - utc_offset) % 24


def _utc_hour_to_local(utc_hour: int, utc_offset: int) -> int:
    """Convert a UTC hour (0-23) to local hour using the UTC offset."""
    return (utc_hour + utc_offset) % 24


@router.message(Command("timezone"))
async def timezone_command_handler(
    message: Message,
    state: FSMContext,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SETTINGS_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    await state.clear()
    if profile.timezone:
        await app_context.send_message(
            text=translate(TIMEZONE_CURRENT, lang, timezone=profile.timezone),
            reply_markup=timezone_keyboard(),
        )
    else:
        await app_context.send_message(
            text=translate(TIMEZONE_NOT_SET, lang),
            reply_markup=timezone_keyboard(),
        )


@router.callback_query(TimezoneCallback.filter())
async def change_timezone_callback(
    callback: CallbackQuery,
    callback_data: TimezoneCallback,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    await callback.answer()

    user_profile_repo = container.horoscope.user_profile_repository()
    timezone_str = _format_utc_offset(callback_data.offset)

    profile = await user_profile_repo.aupdate_timezone(
        telegram_uid=user.telegram_uid,
        timezone=timezone_str,
    )

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SETTINGS_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    await app_context.edit_message(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        message_id=callback.message.message_id,
    )
    await app_context.send_message(
        text=translate(TIMEZONE_CHANGED, lang, timezone=timezone_str),
    )
    logger.info(f"User {user.telegram_uid} changed timezone to {timezone_str}")


@router.message(Command("notification_time"))
async def notification_time_command_handler(
    message: Message,
    state: FSMContext,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SETTINGS_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    if not profile.timezone:
        await app_context.send_message(
            text=translate(NOTIFICATION_TIME_SET_TIMEZONE_FIRST, lang),
        )
        return

    utc_offset = _parse_timezone_offset(profile.timezone)

    await state.clear()
    if profile.notification_hour_utc is not None:
        local_hour = _utc_hour_to_local(
            utc_hour=profile.notification_hour_utc,
            utc_offset=utc_offset,
        )
        await app_context.send_message(
            text=translate(
                NOTIFICATION_TIME_CURRENT,
                lang,
                time=f"{local_hour:02d}:00",
            ),
            reply_markup=notification_hour_keyboard(
                language=lang,
                user_timezone_offset=utc_offset,
            ),
        )
    else:
        await app_context.send_message(
            text=translate(NOTIFICATION_TIME_DEFAULT, lang),
            reply_markup=notification_hour_keyboard(
                language=lang,
                user_timezone_offset=utc_offset,
            ),
        )


@router.callback_query(NotificationHourCallback.filter())
async def change_notification_hour_callback(
    callback: CallbackQuery,
    callback_data: NotificationHourCallback,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    await callback.answer()

    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SETTINGS_NO_PROFILE, lang))
        return

    utc_offset = _parse_timezone_offset(profile.timezone)
    local_hour = callback_data.hour
    utc_hour = _local_hour_to_utc(
        local_hour=local_hour,
        utc_offset=utc_offset,
    )

    profile = await user_profile_repo.aupdate_notification_hour(
        telegram_uid=user.telegram_uid,
        notification_hour_utc=utc_hour,
    )

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SETTINGS_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    await app_context.edit_message(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        message_id=callback.message.message_id,
    )
    await app_context.send_message(
        text=translate(
            NOTIFICATION_TIME_CHANGED,
            lang,
            time=f"{local_hour:02d}:00",
        ),
    )
    logger.info(
        f"User {user.telegram_uid} changed notification time to "
        f"{local_hour:02d}:00 local (UTC hour={utc_hour})"
    )


@router.callback_query(ResetNotificationHourCallback.filter())
async def reset_notification_hour_callback(
    callback: CallbackQuery,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    await callback.answer()

    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aupdate_notification_hour(
        telegram_uid=user.telegram_uid,
        notification_hour_utc=None,
    )

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(SETTINGS_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    await app_context.edit_message(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        message_id=callback.message.message_id,
    )
    await app_context.send_message(
        text=translate(NOTIFICATION_TIME_RESET, lang),
    )
    logger.info(f"User {user.telegram_uid} reset notification time to language default")
