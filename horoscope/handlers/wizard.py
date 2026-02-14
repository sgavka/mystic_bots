import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from asgiref.sync import sync_to_async

from core.containers import container
from core.entities import UserEntity
from horoscope import callbacks
from horoscope.keyboards import language_keyboard
from horoscope.states import WizardStates
from horoscope.messages import (
    ERROR_PROFILE_CREATION_FAILED,
    WIZARD_ASK_DOB,
    WIZARD_ASK_PLACE_OF_BIRTH,
    WIZARD_ASK_PLACE_OF_LIVING,
    WIZARD_CHOOSE_LANGUAGE,
    WIZARD_DOB_IN_FUTURE,
    WIZARD_DOB_TOO_OLD,
    WIZARD_INVALID_CITY,
    WIZARD_INVALID_DATE_FORMAT,
    WIZARD_INVALID_NAME,
    WIZARD_PROFILE_READY,
    WIZARD_WELCOME,
    WIZARD_WELCOME_BACK,
    map_telegram_language,
    translate,
)


logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, user: UserEntity, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if profile:
        lang = profile.preferred_language
        await message.answer(translate(WIZARD_WELCOME_BACK, lang, name=profile.name))
        await state.clear()
        return

    default_lang = map_telegram_language(user.language_code)
    await message.answer(
        translate(WIZARD_CHOOSE_LANGUAGE, default_lang),
        reply_markup=language_keyboard(),
    )
    await state.set_state(WizardStates.WAITING_LANGUAGE)


@router.callback_query(WizardStates.WAITING_LANGUAGE, F.data.startswith(callbacks.LANGUAGE_PREFIX))
async def process_language(callback: CallbackQuery, state: FSMContext, **kwargs):
    await callback.answer()

    lang = callback.data[len(callbacks.LANGUAGE_PREFIX):]
    await state.update_data(preferred_language=lang)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(translate(WIZARD_WELCOME, lang))
    await state.set_state(WizardStates.WAITING_NAME)


@router.message(WizardStates.WAITING_NAME, F.text)
async def process_name(message: Message, state: FSMContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    name = message.text.strip()
    if len(name) < 2 or len(name) > 100:
        await message.answer(translate(WIZARD_INVALID_NAME, lang))
        return

    await state.update_data(name=name)
    await message.answer(translate(WIZARD_ASK_DOB, lang, name=name))
    await state.set_state(WizardStates.WAITING_DATE_OF_BIRTH)


@router.message(WizardStates.WAITING_DATE_OF_BIRTH, F.text)
async def process_date_of_birth(message: Message, state: FSMContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')
    text = message.text.strip()

    try:
        date_of_birth = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(translate(WIZARD_INVALID_DATE_FORMAT, lang))
        return

    today = datetime.now().date()
    if date_of_birth >= today:
        await message.answer(translate(WIZARD_DOB_IN_FUTURE, lang))
        return

    if (today.year - date_of_birth.year) > 150:
        await message.answer(translate(WIZARD_DOB_TOO_OLD, lang))
        return

    await state.update_data(date_of_birth=text)
    await message.answer(translate(WIZARD_ASK_PLACE_OF_BIRTH, lang))
    await state.set_state(WizardStates.WAITING_PLACE_OF_BIRTH)


@router.message(WizardStates.WAITING_PLACE_OF_BIRTH, F.text)
async def process_place_of_birth(message: Message, state: FSMContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    place = message.text.strip()
    if len(place) < 2 or len(place) > 200:
        await message.answer(translate(WIZARD_INVALID_CITY, lang))
        return

    await state.update_data(place_of_birth=place)
    await message.answer(translate(WIZARD_ASK_PLACE_OF_LIVING, lang))
    await state.set_state(WizardStates.WAITING_PLACE_OF_LIVING)


@router.message(WizardStates.WAITING_PLACE_OF_LIVING, F.text)
async def process_place_of_living(message: Message, state: FSMContext, user: UserEntity, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    place = message.text.strip()
    if len(place) < 2 or len(place) > 200:
        await message.answer(translate(WIZARD_INVALID_CITY, lang))
        return

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
            preferred_language=lang,
        )

    try:
        profile = await _create_profile()
    except Exception:
        logger.exception(f"Failed to create profile for user {user.telegram_uid}")
        await state.clear()
        await message.answer(translate(ERROR_PROFILE_CREATION_FAILED, lang))
        return

    await state.clear()

    await message.answer(
        translate(
            WIZARD_PROFILE_READY,
            lang,
            name=profile.name,
            dob=profile.date_of_birth.strftime('%d.%m.%Y'),
            place_of_birth=profile.place_of_birth,
            place_of_living=profile.place_of_living,
        )
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
