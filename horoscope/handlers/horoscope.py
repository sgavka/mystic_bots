import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async

from core.containers import container
from core.entities import UserEntity
from horoscope.keyboards import subscribe_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("horoscope"))
async def view_horoscope_handler(message: Message, user: UserEntity, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    horoscope_repo = container.horoscope.horoscope_repository()
    subscription_repo = container.horoscope.subscription_repository()

    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    if not profile:
        await message.answer(
            "You haven't set up your profile yet.\n"
            "Send /start to begin the onboarding wizard."
        )
        return

    today = date.today()
    horoscope = await horoscope_repo.aget_by_user_and_date(
        telegram_uid=user.telegram_uid,
        target_date=today,
    )

    if not horoscope:
        await message.answer(
            "Your horoscope for today is not ready yet.\n"
            "It will be generated soon. Please check back later."
        )
        return

    @sync_to_async
    def _check_subscription():
        return subscription_repo.has_active_subscription(user.telegram_uid)

    has_subscription = await _check_subscription()

    if has_subscription:
        await message.answer(horoscope.full_text)
    else:
        await message.answer(
            horoscope.teaser_text
            + "\n\nSubscribe to see your full daily horoscope!",
            reply_markup=subscribe_keyboard(),
        )
