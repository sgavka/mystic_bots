import logging
from datetime import date, datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from asgiref.sync import sync_to_async

from django.utils.translation import gettext_lazy as _

from core.containers import container
from core.entities import UserEntity
from horoscope.callbacks import LanguageCallback, SkipBirthTimeCallback
from horoscope.keyboards import language_keyboard, skip_birth_time_keyboard
from horoscope.states import WizardStates
from horoscope.utils import map_telegram_language, parse_date, parse_time, translate
from telegram_bot.app_context import AppContext

WIZARD_CHOOSE_LANGUAGE = _("🌍 Please choose your language:")

WIZARD_WELCOME_BACK = _(
    "👋 Welcome back, <b>{name}</b>!\n"
    "\n"
    "Your profile is already set up. You'll receive your daily horoscope soon ✨"
)

WIZARD_WELCOME = _(
    "✨ Welcome to <b>Mystic Horoscope</b>! ✨\n"
    "\n"
    "🔮 I'll create a personalized horoscope just for you. Let's set up your profile first.\n"
    "\n"
    "What is your <b>name</b>?"
)

WIZARD_INVALID_NAME = _("Please enter a valid name (2-100 characters).")

WIZARD_ASK_DOB = _(
    "😊 Nice to meet you, <b>{name}</b>!\n"
    "\n"
    "📅 Now, please enter your <b>full date of birth</b>.\n"
    "\n"
    "Example: <code>15.03.1990</code>"
)

WIZARD_INVALID_DATE_FORMAT = _(
    "Invalid date format. Accepted formats:\n"
    "<code>DD.MM.YYYY</code>, <code>DD/MM/YYYY</code>, <code>DD-MM-YYYY</code>, <code>YYYY-MM-DD</code>\n"
    "\n"
    "Example: <code>15.03.1990</code>"
)

WIZARD_DOB_IN_FUTURE = _("Date of birth must be in the past. Please try again.")

WIZARD_DOB_TOO_OLD = _("Please enter a valid date of birth.")

WIZARD_ASK_BIRTH_TIME = _(
    "🕐 Do you know your <b>birth time</b>? It helps make the horoscope more precise.\n"
    "\n"
    "Enter time in format <code>HH:MM</code> (e.g. <code>14:30</code>),\n"
    "or press the button below to skip."
)

WIZARD_INVALID_TIME_FORMAT = _(
    "Invalid time format. Please enter time as <code>HH:MM</code> (e.g. <code>14:30</code>),\n"
    "or press the button below to skip."
)

WIZARD_ASK_PLACE_OF_BIRTH = _(
    "🎯 Great! Now, please enter your <b>place of birth</b> (city).\n"
    "\n"
    "Example: <code>London</code>"
)

WIZARD_INVALID_CITY = _("Please enter a valid city name (2-200 characters).")

WIZARD_ASK_PLACE_OF_LIVING = _(
    "📍 Almost done! Please enter your <b>current place of living</b> (city).\n"
    "\n"
    "Example: <code>New York</code>"
)

WIZARD_PROFILE_READY = _(
    "✅ Your profile is ready, <b>{name}</b>!\n"
    "\n"
    "📅 Date of birth: {dob}\n"
    "{birth_time_line}"
    "🏠 Born in: {place_of_birth}\n"
    "📍 Living in: {place_of_living}\n"
    "\n"
    "🔮 Generating your first horoscope... Please wait a moment."
)

WIZARD_BIRTH_TIME_LINE = _("🕐 Birth time: {birth_time}\n")

ERROR_PROFILE_CREATION_FAILED = _("😔 Something went wrong while creating your profile. Please try again with /start")


logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, user: UserEntity, app_context: AppContext, **kwargs):
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)

    if profile:
        lang = profile.preferred_language
        await app_context.send_message(text=translate(WIZARD_WELCOME_BACK, lang, name=profile.name))
        await state.clear()
        return

    default_lang = map_telegram_language(user.language_code)
    await app_context.send_message(
        text=translate(WIZARD_CHOOSE_LANGUAGE, default_lang),
        reply_markup=language_keyboard(),
    )
    await state.set_state(WizardStates.WAITING_LANGUAGE)


@router.callback_query(WizardStates.WAITING_LANGUAGE, LanguageCallback.filter())
async def process_language(
    callback: CallbackQuery,
    callback_data: LanguageCallback,
    state: FSMContext,
    app_context: AppContext,
    **kwargs,
):
    await callback.answer()

    lang = callback_data.code
    await state.update_data(preferred_language=lang)

    await app_context.edit_message(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        message_id=callback.message.message_id,
    )
    await app_context.send_message(text=translate(WIZARD_WELCOME, lang))
    await state.set_state(WizardStates.WAITING_NAME)


@router.message(WizardStates.WAITING_NAME, F.text)
async def process_name(message: Message, state: FSMContext, app_context: AppContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    name = message.text.strip()
    if len(name) < 2 or len(name) > 100:
        await app_context.send_message(text=translate(WIZARD_INVALID_NAME, lang))
        return

    await state.update_data(name=name)
    await app_context.send_message(text=translate(WIZARD_ASK_DOB, lang, name=name))
    await state.set_state(WizardStates.WAITING_DATE_OF_BIRTH)


@router.message(WizardStates.WAITING_DATE_OF_BIRTH, F.text)
async def process_date_of_birth(message: Message, state: FSMContext, app_context: AppContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')
    text = message.text.strip()

    date_of_birth = parse_date(text)
    if not date_of_birth:
        await app_context.send_message(text=translate(WIZARD_INVALID_DATE_FORMAT, lang))
        return

    today = datetime.now().date()
    if date_of_birth >= today:
        await app_context.send_message(text=translate(WIZARD_DOB_IN_FUTURE, lang))
        return

    if (today.year - date_of_birth.year) > 150:
        await app_context.send_message(text=translate(WIZARD_DOB_TOO_OLD, lang))
        return

    await state.update_data(date_of_birth=date_of_birth.isoformat())
    await app_context.send_message(
        text=translate(WIZARD_ASK_BIRTH_TIME, lang),
        reply_markup=skip_birth_time_keyboard(language=lang),
    )
    await state.set_state(WizardStates.WAITING_BIRTH_TIME)


@router.callback_query(WizardStates.WAITING_BIRTH_TIME, SkipBirthTimeCallback.filter())
async def skip_birth_time(
    callback: CallbackQuery,
    state: FSMContext,
    app_context: AppContext,
    **kwargs,
):
    await callback.answer()

    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    await state.update_data(birth_time=None)
    await app_context.edit_message(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        message_id=callback.message.message_id,
    )
    await app_context.send_message(text=translate(WIZARD_ASK_PLACE_OF_BIRTH, lang))
    await state.set_state(WizardStates.WAITING_PLACE_OF_BIRTH)


@router.message(WizardStates.WAITING_BIRTH_TIME, F.text)
async def process_birth_time(message: Message, state: FSMContext, app_context: AppContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    birth_time = parse_time(message.text.strip())
    if not birth_time:
        await app_context.send_message(
            text=translate(WIZARD_INVALID_TIME_FORMAT, lang),
            reply_markup=skip_birth_time_keyboard(language=lang),
        )
        return

    await state.update_data(birth_time=birth_time.isoformat())
    await app_context.send_message(text=translate(WIZARD_ASK_PLACE_OF_BIRTH, lang))
    await state.set_state(WizardStates.WAITING_PLACE_OF_BIRTH)


@router.message(WizardStates.WAITING_PLACE_OF_BIRTH, F.text)
async def process_place_of_birth(message: Message, state: FSMContext, app_context: AppContext, **kwargs):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    place = message.text.strip()
    if len(place) < 2 or len(place) > 200:
        await app_context.send_message(text=translate(WIZARD_INVALID_CITY, lang))
        return

    await state.update_data(place_of_birth=place)
    await app_context.send_message(text=translate(WIZARD_ASK_PLACE_OF_LIVING, lang))
    await state.set_state(WizardStates.WAITING_PLACE_OF_LIVING)


@router.message(WizardStates.WAITING_PLACE_OF_LIVING, F.text)
async def process_place_of_living(
    message: Message,
    state: FSMContext,
    user: UserEntity,
    app_context: AppContext,
    **kwargs,
):
    data = await state.get_data()
    lang = data.get('preferred_language', 'en')

    place = message.text.strip()
    if len(place) < 2 or len(place) > 200:
        await app_context.send_message(text=translate(WIZARD_INVALID_CITY, lang))
        return

    name = data['name']
    date_of_birth = data['date_of_birth']
    birth_time_str = data.get('birth_time')
    place_of_birth = data['place_of_birth']
    place_of_living = place

    user_profile_repo = container.horoscope.user_profile_repository()

    @sync_to_async
    def _create_profile():
        from datetime import time as time_type
        birth_time = time_type.fromisoformat(birth_time_str) if birth_time_str else None
        return user_profile_repo.create_profile(
            telegram_uid=user.telegram_uid,
            name=name,
            date_of_birth=date.fromisoformat(date_of_birth),
            place_of_birth=place_of_birth,
            place_of_living=place_of_living,
            birth_time=birth_time,
            preferred_language=lang,
        )

    try:
        profile = await _create_profile()
    except Exception:
        # Profile creation failure must not crash the wizard — user needs error feedback
        logger.exception(f"Failed to create profile for user {user.telegram_uid}")
        await state.clear()
        await app_context.send_message(text=translate(ERROR_PROFILE_CREATION_FAILED, lang))
        return

    await state.clear()

    birth_time_line = ""
    if profile.birth_time:
        birth_time_line = translate(
            WIZARD_BIRTH_TIME_LINE,
            lang,
            birth_time=profile.birth_time.strftime('%H:%M'),
        )

    await app_context.send_message(
        text=translate(
            WIZARD_PROFILE_READY,
            lang,
            name=profile.name,
            dob=profile.date_of_birth.strftime('%d.%m.%Y'),
            birth_time_line=birth_time_line,
            place_of_birth=profile.place_of_birth,
            place_of_living=profile.place_of_living,
        ),
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
