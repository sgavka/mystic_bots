import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.containers import container
from core.entities import UserEntity
from horoscope.keyboards import subscribe_keyboard
from horoscope.messages import (
    HOROSCOPE_GENERATING,
    HOROSCOPE_NO_PROFILE,
    HOROSCOPE_NOT_READY,
    HOROSCOPE_SUBSCRIBE_CTA,
    map_telegram_language,
    translate,
)

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("horoscope"))
async def view_horoscope_handler(message: Message, user: UserEntity, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()

    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    if not profile:
        lang = map_telegram_language(user.language_code)
        await message.answer(translate(HOROSCOPE_NO_PROFILE, lang))
        return

    lang = profile.preferred_language

    today = date.today()
    horoscope = await horoscope_repo.aget_by_user_and_date(
        telegram_uid=user.telegram_uid,
        target_date=today,
    )

    if not horoscope:
        has_subscription = await subscription_repo.ahas_active_subscription(user.telegram_uid)
        if has_subscription:
            from horoscope.tasks.generate_horoscope import generate_horoscope_task

            generate_horoscope_task.delay(
                telegram_uid=user.telegram_uid,
                target_date=today.isoformat(),
            )
            await message.answer(translate(HOROSCOPE_GENERATING, lang))
        else:
            await message.answer(translate(HOROSCOPE_NOT_READY, lang))
        return

    has_subscription = await subscription_repo.ahas_active_subscription(user.telegram_uid)

    if has_subscription:
        await message.answer(horoscope.full_text)
    else:
        await message.answer(
            horoscope.teaser_text + translate(HOROSCOPE_SUBSCRIBE_CTA, lang),
            reply_markup=subscribe_keyboard(language=lang),
        )
