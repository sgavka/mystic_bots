import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.containers import container
from core.entities import UserEntity
from horoscope.callbacks import LanguageCallback
from horoscope.keyboards import language_keyboard
from horoscope.utils import map_telegram_language, translate
from telegram_bot.app_context import AppContext

LANGUAGE_CURRENT = _(
    "🌍 Your current language: <b>{lang_name}</b>\n"
    "\n"
    "Choose a new language:"
)

LANGUAGE_CHANGED = _("✅ Language changed to <b>English</b> 🇬🇧")

LANGUAGE_NO_PROFILE = _(
    "⚠️ You haven't set up your profile yet.\n"
    "Send /start to begin."
)

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("language"))
async def language_command_handler(
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
        await app_context.send_message(text=translate(LANGUAGE_NO_PROFILE, lang))
        return

    lang = profile.preferred_language
    lang_display = settings.HOROSCOPE_LANGUAGE_NAMES.get(lang, lang)

    await state.clear()
    await app_context.send_message(
        text=translate(LANGUAGE_CURRENT, lang, lang_name=lang_display),
        reply_markup=language_keyboard(current_language=lang),
    )


@router.callback_query(LanguageCallback.filter())
async def change_language_callback(
    callback: CallbackQuery,
    callback_data: LanguageCallback,
    state: FSMContext,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    await callback.answer()

    new_lang = callback_data.code

    user_profile_repo = container.horoscope.user_profile_repository()

    profile = await user_profile_repo.aupdate_language(
        telegram_uid=user.telegram_uid,
        language=new_lang,
    )

    if not profile:
        lang = map_telegram_language(user.language_code)
        await app_context.send_message(text=translate(LANGUAGE_NO_PROFILE, lang))
        return

    await app_context.edit_message(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        message_id=callback.message.message_id,
    )
    await app_context.send_message(text=translate(LANGUAGE_CHANGED, new_lang))
    logger.info(f"User {user.telegram_uid} changed language to {new_lang}")
