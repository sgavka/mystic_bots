from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.entities import UserEntity


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, user: UserEntity, **kwargs):
    await message.answer(
        f"Welcome, <b>{user.full_name}</b>!\n\n"
        "I'm your personal horoscope bot. "
        "Let me set up your profile to generate personalized horoscopes."
    )
