from typing import Any

from django.utils.translation import gettext
from django.utils.translation import override as translation_override

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

# Mapping from translation keys to English msgid strings (used as gettext keys in .po files)
_KEY_TO_MSGID = {
    "wizard.choose_language": "🌍 Please choose your language:",
    "wizard.welcome_back": (
        "👋 Welcome back, <b>{name}</b>!\n"
        "\n"
        "Your profile is already set up. You'll receive your daily horoscope soon ✨"
    ),
    "wizard.welcome": (
        "✨ Welcome to <b>Mystic Horoscope</b>! ✨\n"
        "\n"
        "🔮 I'll create a personalized horoscope just for you. Let's set up your profile first.\n"
        "\n"
        "What is your <b>name</b>?"
    ),
    "wizard.invalid_name": "Please enter a valid name (2-100 characters).",
    "wizard.ask_dob": (
        "😊 Nice to meet you, <b>{name}</b>!\n"
        "\n"
        "📅 Now, please enter your <b>full date of birth</b>\n"
        "in format: <code>DD.MM.YYYY</code>\n"
        "\n"
        "Example: <code>15.03.1990</code>"
    ),
    "wizard.invalid_date_format": (
        "Invalid date format. Please use <code>DD.MM.YYYY</code>\n"
        "\n"
        "Example: <code>15.03.1990</code>"
    ),
    "wizard.dob_in_future": "Date of birth must be in the past. Please try again.",
    "wizard.dob_too_old": "Please enter a valid date of birth.",
    "wizard.ask_place_of_birth": (
        "🎯 Great! Now, please enter your <b>place of birth</b> (city).\n"
        "\n"
        "Example: <code>London</code>"
    ),
    "wizard.invalid_city": "Please enter a valid city name (2-200 characters).",
    "wizard.ask_place_of_living": (
        "📍 Almost done! Please enter your <b>current place of living</b> (city).\n"
        "\n"
        "Example: <code>New York</code>"
    ),
    "wizard.profile_ready": (
        "✅ Your profile is ready, <b>{name}</b>!\n"
        "\n"
        "📅 Date of birth: {dob}\n"
        "🏠 Born in: {place_of_birth}\n"
        "📍 Living in: {place_of_living}\n"
        "\n"
        "🔮 Generating your first horoscope... Please wait a moment."
    ),
    "horoscope.no_profile": (
        "⚠️ You haven't set up your profile yet.\n"
        "Send /start to begin the onboarding wizard."
    ),
    "horoscope.not_ready": (
        "⏳ Your horoscope for today is not ready yet.\n"
        "It will be generated soon. Please check back later."
    ),
    "horoscope.subscribe_cta": (
        "\n"
        "\n"
        "🔒 Subscribe to see your full daily horoscope!"
    ),
    "subscription.offer": (
        "⭐ Subscribe for <b>{days} days</b> of full daily horoscope access.\n"
        "\n"
        "💰 Price: <b>{price} Telegram Stars</b>\n"
        "\n"
        "Tap the button below to pay."
    ),
    "subscription.invoice_title": "Horoscope Subscription",
    "subscription.invoice_description": "{days}-day access to full daily horoscope",
    "subscription.payment_success": (
        "✅ Payment successful! Your subscription is now active.\n"
        "\n"
        "📅 Expires: {expires}\n"
        "\n"
        "Use /horoscope to see your full daily horoscope ✨"
    ),
    "keyboard.subscribe": "⭐ Subscribe for full horoscope",
    "task.first_horoscope_ready": (
        "🔮 Your first horoscope is ready!\n"
        "\n"
        "{text}"
    ),
    "task.expiry_reminder": (
        "⏰ Your horoscope subscription expires in <b>{days} day(s)</b>.\n"
        "\n"
        "Renew now to keep receiving your full daily horoscope! ✨"
    ),
    "task.subscription_expired": (
        "⚠️ Your horoscope subscription has <b>expired</b>.\n"
        "\n"
        "You'll now see a preview of your daily horoscope. Subscribe again to get full access! ⭐"
    ),
    "language.current": (
        "🌍 Your current language: <b>{lang_name}</b>\n"
        "\n"
        "Choose a new language:"
    ),
    "language.changed": "✅ Language changed to <b>English</b> 🇬🇧",
    "language.no_profile": (
        "⚠️ You haven't set up your profile yet.\n"
        "Send /start to begin."
    ),
    "horoscope.header": "Horoscope for {sign} — {date}",
    "horoscope.greeting": "Dear {name},",
    "error.profile_creation_failed": "😔 Something went wrong while creating your profile. Please try again with /start",
    "error.payment_failed": "😔 Something went wrong while activating your subscription. Please contact support if the issue persists.",
}


def t(key: str, language: str, **kwargs: Any) -> str:
    """Get translated string by key and language code, with optional formatting."""
    msgid = _KEY_TO_MSGID.get(key)
    if not msgid:
        return key

    with translation_override(language):
        text = gettext(msgid)

    if kwargs:
        text = text.format(**kwargs)

    return text


SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk', 'de'}


def map_telegram_language(language_code: str | None) -> str:
    """Map Telegram's language_code to our supported language code."""
    if not language_code:
        return 'en'
    code = language_code.lower().split('-')[0]
    if code in SUPPORTED_LANGUAGE_CODES:
        return code
    return 'en'
