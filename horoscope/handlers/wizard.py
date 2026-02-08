import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from asgiref.sync import sync_to_async

from core.containers import container
from core.entities import UserEntity
from horoscope.states import WizardStates


logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, user: UserEntity, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if profile:
        await message.answer(
            f"Welcome back, <b>{profile.name}</b>!\n\n"
            "Your profile is already set up. "
            "You'll receive your daily horoscope soon."
        )
        await state.clear()
        return

    await message.answer(
        "Welcome to <b>Mystic Horoscope</b>!\n\n"
        "I'll create a personalized horoscope just for you. "
        "Let's set up your profile first.\n\n"
        "What is your <b>name</b>?"
    )
    await state.set_state(WizardStates.WAITING_NAME)


@router.message(WizardStates.WAITING_NAME, F.text)
async def process_name(message: Message, state: FSMContext, **kwargs):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 100:
        await message.answer("Please enter a valid name (2-100 characters).")
        return

    await state.update_data(name=name)
    await message.answer(
        f"Nice to meet you, <b>{name}</b>!\n\n"
        "Now, please enter your <b>full date of birth</b>\n"
        "in format: <code>DD.MM.YYYY</code>\n\n"
        "Example: <code>15.03.1990</code>"
    )
    await state.set_state(WizardStates.WAITING_DATE_OF_BIRTH)


@router.message(WizardStates.WAITING_DATE_OF_BIRTH, F.text)
async def process_date_of_birth(message: Message, state: FSMContext, **kwargs):
    text = message.text.strip()

    try:
        date_of_birth = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(
            "Invalid date format. Please use <code>DD.MM.YYYY</code>\n\n"
            "Example: <code>15.03.1990</code>"
        )
        return

    today = datetime.now().date()
    if date_of_birth >= today:
        await message.answer("Date of birth must be in the past. Please try again.")
        return

    if (today.year - date_of_birth.year) > 150:
        await message.answer("Please enter a valid date of birth.")
        return

    await state.update_data(date_of_birth=text)
    await message.answer(
        "Great! Now, please enter your <b>place of birth</b> (city).\n\n"
        "Example: <code>London</code>"
    )
    await state.set_state(WizardStates.WAITING_PLACE_OF_BIRTH)


@router.message(WizardStates.WAITING_PLACE_OF_BIRTH, F.text)
async def process_place_of_birth(message: Message, state: FSMContext, **kwargs):
    place = message.text.strip()
    if len(place) < 2 or len(place) > 200:
        await message.answer("Please enter a valid city name (2-200 characters).")
        return

    await state.update_data(place_of_birth=place)
    await message.answer(
        "Almost done! Please enter your <b>current place of living</b> (city).\n\n"
        "Example: <code>New York</code>"
    )
    await state.set_state(WizardStates.WAITING_PLACE_OF_LIVING)


@router.message(WizardStates.WAITING_PLACE_OF_LIVING, F.text)
async def process_place_of_living(message: Message, state: FSMContext, user: UserEntity, **kwargs):
    place = message.text.strip()
    if len(place) < 2 or len(place) > 200:
        await message.answer("Please enter a valid city name (2-200 characters).")
        return

    data = await state.get_data()
    name = data['name']
    date_of_birth = data['date_of_birth']
    place_of_birth = data['place_of_birth']
    place_of_living = place

    user_profile_repo = container.horoscope.user_profile_repository()

    @sync_to_async
    def _create_profile():
        return user_profile_repo.create_profile(
            telegram_uid=user.telegram_uid,
            name=name,
            date_of_birth=datetime.strptime(date_of_birth, "%d.%m.%Y").date(),
            place_of_birth=place_of_birth,
            place_of_living=place_of_living,
        )

    profile = await _create_profile()

    await state.clear()

    await message.answer(
        f"Your profile is ready, <b>{profile.name}</b>!\n\n"
        f"Date of birth: {profile.date_of_birth.strftime('%d.%m.%Y')}\n"
        f"Born in: {profile.place_of_birth}\n"
        f"Living in: {profile.place_of_living}\n\n"
        "Generating your first horoscope... Please wait a moment."
    )

    # Trigger Celery task to generate first horoscope
    from horoscope.tasks import generate_horoscope_task
    today = datetime.now().date()
    generate_horoscope_task.delay(
        telegram_uid=user.telegram_uid,
        target_date=today.isoformat(),
        horoscope_type='first',
    )
    logger.info(f"First horoscope generation task queued for user {user.telegram_uid}")
