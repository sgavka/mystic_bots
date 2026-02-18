"""
Django settings for Mystic Bots project.
"""

import logging as _logging
import os
from pathlib import Path

from core.enums import BotSlug

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key secret in production!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'core',
    'telegram_bot',
    'horoscope',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_DATABASE', 'postgres'),
        'USER': os.environ.get('DB_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Russian'),
    ('uk', 'Ukrainian'),
    ('de', 'German'),
    ('hi', 'Hindi'),
    ('ar', 'Arabic'),
    ('it', 'Italian'),
    ('fr', 'French'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files

STATIC_URL = 'static/'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Redis configuration

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_BOT_DB = int(os.environ.get('REDIS_BOT_DB', 0))


# Background scheduler configuration

SCHEDULER_DAILY_INTERVAL_SECONDS = int(os.environ.get('SCHEDULER_DAILY_INTERVAL_SECONDS', str(60 * 60 * 24)))


# Bot configuration

MAIN_BOT_SLUG = os.environ.get('MAIN_BOT_SLUG', 'horoscope')


def _get_bot_config(slug: str) -> dict:
    """Get bot configuration from environment variables."""
    slug_upper = slug.upper().replace('-', '_')
    return {
        'slug': slug,
        'token': os.environ.get(f'BOT_{slug_upper}_TOKEN', ''),
        'title': os.environ.get(f'BOT_{slug_upper}_TITLE', slug.title()),
    }


BOTS_CONFIG = {slug.value: _get_bot_config(slug.value) for slug in BotSlug}

# Current bot config (set at runtime by start_bot command)
CURRENT_BOT_SLUG: BotSlug = BotSlug(MAIN_BOT_SLUG)
CURRENT_BOT_TOKEN = BOTS_CONFIG.get(MAIN_BOT_SLUG, {}).get('token', '')

# Admin configuration
ADMIN_USERS_IDS = [
    int(uid.strip()) for uid in os.environ.get('ADMIN_USERS_IDS', '').split(',')
    if uid.strip() and uid.strip().isdigit()
]
_reports_chat_id = os.environ.get('REPORTS_CHAT_ID', '')
REPORTS_CHAT_ID = int(_reports_chat_id) if _reports_chat_id and _reports_chat_id.lstrip('-').isdigit() else None


# Horoscope configuration

_DEFAULT_HOROSCOPE_LANGUAGES = 'en:English:🇬🇧,ru:Русский:🇷🇺,uk:Українська:🇺🇦,de:Deutsch:🇩🇪,hi:हिन्दी:🇮🇳,ar:العربية:🇸🇦,it:Italiano:🇮🇹,fr:Français:🇫🇷'


def _parse_horoscope_languages(raw: str) -> tuple[dict[str, str], dict[str, str]]:
    """Parse HOROSCOPE_LANGUAGES env var into (names, flags) dicts."""
    names = {}
    flags = {}
    for entry in raw.split(','):
        parts = entry.strip().split(':')
        if len(parts) >= 2:
            code = parts[0].strip()
            name = parts[1].strip()
            flag = parts[2].strip() if len(parts) >= 3 else ''
            names[code] = name
            flags[code] = flag
    return names, flags


HOROSCOPE_LANGUAGE_NAMES, HOROSCOPE_LANGUAGE_FLAGS = _parse_horoscope_languages(
    os.environ.get('HOROSCOPE_LANGUAGES', _DEFAULT_HOROSCOPE_LANGUAGES)
)
HOROSCOPE_SUPPORTED_LANGUAGE_CODES = set(HOROSCOPE_LANGUAGE_NAMES.keys())

HOROSCOPE_SUBSCRIPTION_PRICE_STARS = int(os.environ.get('HOROSCOPE_SUBSCRIPTION_PRICE_STARS', '1'))
HOROSCOPE_SUBSCRIPTION_DURATION_DAYS = int(os.environ.get('HOROSCOPE_SUBSCRIPTION_DURATION_DAYS', '90'))
HOROSCOPE_SUBSCRIPTION_REMINDER_DAYS = int(os.environ.get('HOROSCOPE_SUBSCRIPTION_REMINDER_DAYS', '3'))
HOROSCOPE_TEASER_LINE_COUNT = int(os.environ.get('HOROSCOPE_TEASER_LINE_COUNT', '3'))
HOROSCOPE_EXTENDED_TEASER_LINE_COUNT = int(os.environ.get('HOROSCOPE_EXTENDED_TEASER_LINE_COUNT', '8'))
HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS = int(os.environ.get('HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS', '10'))
HOROSCOPE_ACTIVITY_WINDOW_DAYS = int(os.environ.get('HOROSCOPE_ACTIVITY_WINDOW_DAYS', '5'))


# LLM configuration

LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4o-mini')
LLM_BASE_URL = os.environ.get('LLM_BASE_URL', '')
LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', '30'))


# Grafana Loki logging configuration (optional)

LOKI_URL = os.environ.get('LOKI_URL', '')
LOKI_BEARER_TOKEN = os.environ.get('LOKI_BEARER_TOKEN', '')
LOKI_APPLICATION_NAME = os.environ.get('LOKI_APPLICATION_NAME', '')
LOKI_ENABLED = all([LOKI_URL, LOKI_BEARER_TOKEN, LOKI_APPLICATION_NAME])


# Logging configuration

_loki_handler = {
    'level': 'WARNING',
    'class': 'core.loki_logger.LokiHandlerWrapper',
    'formatter': 'loki',
}

_handlers_list = ['console', 'loki'] if LOKI_ENABLED else ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'loki': {
            'format': '{message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        **(
            {'loki': _loki_handler} if LOKI_ENABLED else {}
        ),
    },
    'root': {
        'handlers': _handlers_list,
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': _handlers_list,
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Startup validation
_startup_logger = _logging.getLogger(__name__)

if not CURRENT_BOT_TOKEN:
    _startup_logger.warning("BOT token is not set. Set BOT_HOROSCOPE_TOKEN environment variable.")

if DATABASES['default']['PASSWORD'] == 'postgres' and not DEBUG:
    _startup_logger.warning("Database password is using default value in non-debug mode.")
