import re
from datetime import date, datetime, time
from typing import Any, Optional

from django.conf import settings
from django.utils.translation import gettext
from django.utils.translation import override as translation_override

ZODIAC_SIGNS = {
    (1, 20): "Aquarius", (2, 19): "Pisces", (3, 21): "Aries",
    (4, 20): "Taurus", (5, 21): "Gemini", (6, 21): "Cancer",
    (7, 23): "Leo", (8, 23): "Virgo", (9, 23): "Libra",
    (10, 23): "Scorpio", (11, 22): "Sagittarius", (12, 22): "Capricorn",
}


def get_zodiac_sign(date_of_birth: date) -> str:
    month = date_of_birth.month
    day = date_of_birth.day

    boundaries = sorted(ZODIAC_SIGNS.keys())
    for i, (m, d) in enumerate(boundaries):
        if month == m and day < d:
            prev_idx = (i - 1) % len(boundaries)
            return ZODIAC_SIGNS[boundaries[prev_idx]]
        elif month == m and day >= d:
            return ZODIAC_SIGNS[(m, d)]

    return "Capricorn"


def translate(msgid: str, language: str, **kwargs: Any) -> str:
    """Translate a message string using Django gettext with language override."""
    with translation_override(language):
        text = gettext(msgid)
    if kwargs:
        text = text.format(**kwargs)
    return text


DATE_FORMATS = [
    "%d.%m.%Y",   # DD.MM.YYYY (15.03.1990)
    "%d/%m/%Y",   # DD/MM/YYYY (15/03/1990)
    "%d-%m-%Y",   # DD-MM-YYYY (15-03-1990)
    "%Y-%m-%d",   # YYYY-MM-DD (1990-03-15)
    "%Y/%m/%d",   # YYYY/MM/DD (1990/03/15)
    "%Y.%m.%d",   # YYYY.MM.DD (1990.03.15)
]


def parse_date(text: str) -> Optional[date]:
    """Parse a date string trying multiple common formats.

    Returns date object if parsing succeeds, None otherwise.
    """
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


TIME_FORMATS = [
    "%H:%M",     # 24-hour: 14:30
    "%H.%M",     # 24-hour with dot: 14.30
    "%I:%M %p",  # 12-hour: 2:30 PM
    "%I:%M%p",   # 12-hour no space: 2:30PM
]


def parse_time(text: str) -> Optional[time]:
    """Parse a time string trying multiple common formats.

    Returns time object if parsing succeeds, None otherwise.
    """
    text = text.strip()
    # Normalize whitespace around AM/PM
    text = re.sub(r'\s*(AM|PM|am|pm)\s*', r' \1', text).strip()
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def map_telegram_language(language_code: str | None) -> str:
    """Map Telegram's language_code to our supported language code."""
    if not language_code:
        return 'en'
    code = language_code.lower().split('-')[0]
    if code in settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES:
        return code
    return 'en'
