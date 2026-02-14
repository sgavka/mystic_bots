import logging
from datetime import date

from aiogram import F, Router
from aiogram.types import Message

from django.utils.translation import gettext_lazy as _

from core.containers import container
from core.entities import UserEntity
from horoscope.utils import translate
from telegram_bot.app_context import AppContext

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text)
async def handle_followup_question(
    message: Message,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    question_text = message.text
    if not question_text:
        return

    subscription_repo = container.horoscope.subscription_repository()
    has_subscription = await subscription_repo.ahas_active_subscription(user.telegram_uid)
    if not has_subscription:
        return

    horoscope_repo = container.horoscope.horoscope_repository()
    today = date.today()
    horoscope = await horoscope_repo.aget_by_user_and_date(
        telegram_uid=user.telegram_uid,
        target_date=today,
    )
    if not horoscope:
        return

    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    lang = profile.preferred_language if profile else 'en'

    followup_repo = container.horoscope.followup_repository()
    previous_followups = await followup_repo.aget_by_horoscope(horoscope.id)

    from horoscope.services.llm import LLMService

    llm_service = LLMService()
    try:
        result = llm_service.generate_followup_answer(
            horoscope_text=horoscope.full_text,
            question=question_text,
            language=lang,
            previous_followups=previous_followups,
        )
    except Exception as e:
        # LLM failure must not break the flow — best-effort delivery
        logger.error("Failed to generate followup answer", exc_info=e)
        await app_context.send_message(
            text=translate(_(
                "😔 Sorry, I couldn't generate an answer right now. Please try again later."
            ), lang),
        )
        return

    await followup_repo.acreate_followup(
        horoscope_id=horoscope.id,
        question_text=question_text,
        answer_text=result.answer_text,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )

    await app_context.send_message(text=result.answer_text)
