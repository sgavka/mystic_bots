from typing import Any

from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.utils.translation import override as translation_override


# ---------------------------------------------------------------------------
# Language configuration
# ---------------------------------------------------------------------------

LANGUAGE_NAMES = {
    'en': "English",
    'ru': "Русский",
    'uk': "Українська",
    'de': "Deutsch",
}

LANGUAGE_FLAGS = {
    'en': "🇬🇧",
    'ru': "🇷🇺",
    'uk': "🇺🇦",
    'de': "🇩🇪",
}

SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk', 'de'}


def map_telegram_language(language_code: str | None) -> str:
    """Map Telegram's language_code to our supported language code."""
    if not language_code:
        return 'en'
    code = language_code.lower().split('-')[0]
    if code in SUPPORTED_LANGUAGE_CODES:
        return code
    return 'en'


# ---------------------------------------------------------------------------
# Translation helper
# ---------------------------------------------------------------------------

def translate(msgid: str, language: str, **kwargs: Any) -> str:
    """Translate a message string using Django gettext with language override."""
    with translation_override(language):
        text = gettext(msgid)
    if kwargs:
        text = text.format(**kwargs)
    return text


# ---------------------------------------------------------------------------
# Translatable message constants (English msgids for gettext .po files)
# ---------------------------------------------------------------------------

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
    "📅 Now, please enter your <b>full date of birth</b>\n"
    "in format: <code>DD.MM.YYYY</code>\n"
    "\n"
    "Example: <code>15.03.1990</code>"
)

WIZARD_INVALID_DATE_FORMAT = _(
    "Invalid date format. Please use <code>DD.MM.YYYY</code>\n"
    "\n"
    "Example: <code>15.03.1990</code>"
)

WIZARD_DOB_IN_FUTURE = _("Date of birth must be in the past. Please try again.")

WIZARD_DOB_TOO_OLD = _("Please enter a valid date of birth.")

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
    "🏠 Born in: {place_of_birth}\n"
    "📍 Living in: {place_of_living}\n"
    "\n"
    "🔮 Generating your first horoscope... Please wait a moment."
)

HOROSCOPE_NO_PROFILE = _(
    "⚠️ You haven't set up your profile yet.\n"
    "Send /start to begin the onboarding wizard."
)

HOROSCOPE_NOT_READY = _(
    "⏳ Your horoscope for today is not ready yet.\n"
    "It will be generated soon. Please check back later."
)

HOROSCOPE_GENERATING = _(
    "🔮 Your horoscope is being generated right now!\n"
    "Please check back in a minute."
)

HOROSCOPE_SUBSCRIBE_CTA = _(
    "\n"
    "\n"
    "🔒 Subscribe to see your full daily horoscope!"
)

SUBSCRIPTION_OFFER = _(
    "⭐ Subscribe for <b>{days} days</b> of full daily horoscope access.\n"
    "\n"
    "💰 Price: <b>{price} Telegram Stars</b>\n"
    "\n"
    "Tap the button below to pay."
)

SUBSCRIPTION_INVOICE_TITLE = _("Horoscope Subscription")

SUBSCRIPTION_INVOICE_DESCRIPTION = _("{days}-day access to full daily horoscope")

SUBSCRIPTION_PAYMENT_SUCCESS = _(
    "✅ Payment successful! Your subscription is now active.\n"
    "\n"
    "📅 Expires: {expires}\n"
    "\n"
    "Use /horoscope to see your full daily horoscope ✨"
)

KEYBOARD_SUBSCRIBE = _("⭐ Subscribe for full horoscope")

TASK_FIRST_HOROSCOPE_READY = _(
    "🔮 Your first horoscope is ready!\n"
    "\n"
    "{text}"
)

TASK_EXPIRY_REMINDER = _(
    "⏰ Your horoscope subscription expires in <b>{days} day(s)</b>.\n"
    "\n"
    "Renew now to keep receiving your full daily horoscope! ✨"
)

TASK_SUBSCRIPTION_EXPIRED = _(
    "⚠️ Your horoscope subscription has <b>expired</b>.\n"
    "\n"
    "You'll now see a preview of your daily horoscope. Subscribe again to get full access! ⭐"
)

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

HOROSCOPE_HEADER = _("Horoscope for {sign} — {date}")

HOROSCOPE_GREETING = _("Dear {name},")

ERROR_PROFILE_CREATION_FAILED = _("😔 Something went wrong while creating your profile. Please try again with /start")

ERROR_PAYMENT_FAILED = _("😔 Something went wrong while activating your subscription. Please contact support if the issue persists.")
