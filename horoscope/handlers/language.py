import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async

from core.containers import container
from core.entities import UserEntity
from horoscope import callbacks
from horoscope.keyboards import language_keyboard
from horoscope.translations import LANGUAGE_NAMES, t

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("language"))
async def language_command_handler(message: Message, state: FSMContext, user: UserEntity, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if not profile:
        await message.answer(t("language.no_profile", 'en'))
        return

    lang = profile.preferred_language
    lang_display = LANGUAGE_NAMES.get(lang, lang)

    await state.clear()
    await message.answer(
        t("language.current", lang, lang_name=lang_display),
        reply_markup=language_keyboard(current_language=lang),
    )


@router.callback_query(F.data.startswith(callbacks.LANGUAGE_PREFIX))
async def change_language_callback(callback: CallbackQuery, state: FSMContext, user: UserEntity, **kwargs):
    await callback.answer()

    new_lang = callback.data[len(callbacks.LANGUAGE_PREFIX):]

    user_profile_repo = container.horoscope.user_profile_repository()

    @sync_to_async
    def _update_lang():
        return user_profile_repo.update_language(
            telegram_uid=user.telegram_uid,
            language=new_lang,
        )

    profile = await _update_lang()

    if not profile:
        await callback.message.answer(t("language.no_profile", 'en'))
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t("language.changed", new_lang))
    logger.info(f"User {user.telegram_uid} changed language to {new_lang}")
