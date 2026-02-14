import logging
from datetime import date

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from django.utils.translation import gettext_lazy as _

from core.containers import container
from core.entities import UserEntity
from horoscope import callbacks
from horoscope.keyboards import ask_followup_keyboard
from horoscope.states import HoroscopeStates
from horoscope.utils import translate
from telegram_bot.app_context import AppContext

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == callbacks.ASK_FOLLOWUP)
async def ask_followup_callback(
    callback: CallbackQuery,
    state: FSMContext,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    subscription_repo = container.horoscope.subscription_repository()
    has_subscription = await subscription_repo.ahas_active_subscription(user.telegram_uid)

    if not has_subscription:
        await callback.answer()
        return

    horoscope_repo = container.horoscope.horoscope_repository()
    today = date.today()
    horoscope = await horoscope_repo.aget_by_user_and_date(
        telegram_uid=user.telegram_uid,
        target_date=today,
    )

    if not horoscope:
        await callback.answer()
        return

    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    await state.set_state(HoroscopeStates.WAITING_FOLLOWUP_QUESTION)
    await state.update_data(horoscope_id=horoscope.id)

    await callback.answer()
    await app_context.send_message(
        text=translate(_(
            "❓ Ask your question about today's horoscope.\n"
            "Type your question below:"
        ), lang),
    )


@router.message(StateFilter(HoroscopeStates.WAITING_FOLLOWUP_QUESTION))
async def handle_followup_question(
    message: Message,
    state: FSMContext,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    question_text = message.text
    if not question_text:
        return

    fsm_data = await state.get_data()
    horoscope_id = fsm_data.get('horoscope_id')

    horoscope_repo = container.horoscope.horoscope_repository()
    try:
        horoscope = await horoscope_repo.aget(horoscope_id)
    except Exception:
        await state.clear()
        return

    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    from horoscope.services.llm import LLMService

    llm_service = LLMService()
    try:
        result = llm_service.generate_followup_answer(
            horoscope_text=horoscope.full_text,
            question=question_text,
            language=lang,
        )
    except Exception as e:
        # LLM failure must not break the flow — best-effort delivery
        logger.error("Failed to generate followup answer", exc_info=e)
        await app_context.send_message(
            text=translate(_(
                "😔 Sorry, I couldn't generate an answer right now. Please try again later."
            ), lang),
        )
        await state.clear()
        return

    followup_repo = container.horoscope.followup_repository()
    await followup_repo.acreate_followup(
        horoscope_id=horoscope.id,
        question_text=question_text,
        answer_text=result.answer_text,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )

    await app_context.send_message(
        text=result.answer_text,
        reply_markup=ask_followup_keyboard(language=lang),
    )
