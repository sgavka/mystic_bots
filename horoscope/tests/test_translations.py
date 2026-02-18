"""
Tests for the translation system and background tasks.
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.conf import settings
from django.utils import timezone

from django.utils.translation import gettext_lazy as _

from horoscope.handlers.language import LANGUAGE_CHANGED, LANGUAGE_CURRENT, LANGUAGE_NO_PROFILE
from horoscope.handlers.subscription import (
    ERROR_PAYMENT_FAILED,
    SUBSCRIPTION_INVOICE_DESCRIPTION,
    SUBSCRIPTION_INVOICE_TITLE,
    SUBSCRIPTION_OFFER,
    SUBSCRIPTION_PAYMENT_SUCCESS,
)
from horoscope.handlers.wizard import (
    ERROR_PROFILE_CREATION_FAILED,
    WIZARD_ASK_BIRTH_TIME,
    WIZARD_ASK_DOB,
    WIZARD_ASK_PLACE_OF_BIRTH,
    WIZARD_ASK_PLACE_OF_LIVING,
    WIZARD_BIRTH_TIME_LINE,
    WIZARD_CHOOSE_LANGUAGE,
    WIZARD_DOB_IN_FUTURE,
    WIZARD_DOB_TOO_OLD,
    WIZARD_INVALID_CITY,
    WIZARD_INVALID_DATE_FORMAT,
    WIZARD_INVALID_NAME,
    WIZARD_INVALID_TIME_FORMAT,
    WIZARD_PROFILE_READY,
    WIZARD_WELCOME,
    WIZARD_WELCOME_BACK,
)
from horoscope.keyboards import KEYBOARD_SKIP_BIRTH_TIME, KEYBOARD_SUBSCRIBE
from horoscope.tasks.generate_horoscope import TASK_FIRST_HOROSCOPE_READY
from horoscope.tasks.subscription_reminders import TASK_EXPIRY_REMINDER, TASK_SUBSCRIPTION_EXPIRED
from horoscope.utils import map_telegram_language, parse_date, translate

_ALL_MESSAGE_CONSTANTS = [
    WIZARD_CHOOSE_LANGUAGE, WIZARD_WELCOME_BACK, WIZARD_WELCOME,
    WIZARD_INVALID_NAME, WIZARD_ASK_DOB, WIZARD_INVALID_DATE_FORMAT,
    WIZARD_DOB_IN_FUTURE, WIZARD_DOB_TOO_OLD, WIZARD_ASK_BIRTH_TIME,
    WIZARD_INVALID_TIME_FORMAT, WIZARD_BIRTH_TIME_LINE,
    WIZARD_ASK_PLACE_OF_BIRTH,
    WIZARD_INVALID_CITY, WIZARD_ASK_PLACE_OF_LIVING, WIZARD_PROFILE_READY,
    _(
        "⚠️ You haven't set up your profile yet.\n"
        "Send /start to begin the onboarding wizard."
    ),
    _(
        "⏳ Your horoscope for today is not ready yet.\n"
        "It will be generated soon. Please check back later."
    ),
    _(
        "🔮 Your horoscope is being generated right now!\n"
        "Please check back in a minute."
    ),
    _(
        "\n"
        "\n"
        "🔒 Subscribe to see your full daily horoscope!"
    ),
    SUBSCRIPTION_OFFER, SUBSCRIPTION_INVOICE_TITLE,
    SUBSCRIPTION_INVOICE_DESCRIPTION, SUBSCRIPTION_PAYMENT_SUCCESS,
    KEYBOARD_SUBSCRIBE, KEYBOARD_SKIP_BIRTH_TIME,
    TASK_FIRST_HOROSCOPE_READY, TASK_EXPIRY_REMINDER,
    TASK_SUBSCRIPTION_EXPIRED, LANGUAGE_CURRENT, LANGUAGE_CHANGED,
    LANGUAGE_NO_PROFILE,
    ERROR_PROFILE_CREATION_FAILED, ERROR_PAYMENT_FAILED,
]


class TestTranslationFunction:
    def test_basic_translation_en(self):
        result = translate(WIZARD_WELCOME, "en")
        assert "Mystic Horoscope" in result

    def test_basic_translation_ru(self):
        result = translate(WIZARD_WELCOME, "ru")
        assert "Mystic Horoscope" in result
        assert "зовут" in result.lower()

    def test_basic_translation_uk(self):
        result = translate(WIZARD_WELCOME, "uk")
        assert "звати" in result.lower()

    def test_basic_translation_de(self):
        result = translate(WIZARD_WELCOME, "de")
        assert "Willkommen" in result

    def test_basic_translation_hi(self):
        result = translate(WIZARD_WELCOME, "hi")
        assert "स्वागत" in result

    def test_basic_translation_ar(self):
        result = translate(WIZARD_WELCOME, "ar")
        assert "مرحبًا" in result

    def test_basic_translation_it(self):
        result = translate(WIZARD_WELCOME, "it")
        assert "Benvenuto" in result

    def test_basic_translation_fr(self):
        result = translate(WIZARD_WELCOME, "fr")
        assert "Bienvenue" in result

    def test_unsupported_language_falls_back_to_en(self):
        result = translate(WIZARD_WELCOME, "ja")
        en_result = translate(WIZARD_WELCOME, "en")
        assert result == en_result

    def test_formatting_kwargs(self):
        result = translate(WIZARD_WELCOME_BACK, "en", name="Alice")
        assert "Alice" in result

    def test_formatting_kwargs_ru(self):
        result = translate(WIZARD_WELCOME_BACK, "ru", name="Алиса")
        assert "Алиса" in result

    def test_expiry_reminder_formatting(self):
        result = translate(TASK_EXPIRY_REMINDER, "en", days=3)
        assert "3" in result

    def test_subscription_offer_formatting(self):
        result = translate(SUBSCRIPTION_OFFER, "en", days=30, price=100)
        assert "30" in result
        assert "100" in result


class TestMapTelegramLanguage:
    def test_russian(self):
        assert map_telegram_language("ru") == "ru"

    def test_ukrainian(self):
        assert map_telegram_language("uk") == "uk"

    def test_german(self):
        assert map_telegram_language("de") == "de"

    def test_hindi(self):
        assert map_telegram_language("hi") == "hi"

    def test_arabic(self):
        assert map_telegram_language("ar") == "ar"

    def test_italian(self):
        assert map_telegram_language("it") == "it"

    def test_french(self):
        assert map_telegram_language("fr") == "fr"

    def test_english(self):
        assert map_telegram_language("en") == "en"

    def test_none_defaults_to_en(self):
        assert map_telegram_language(None) == "en"

    def test_unsupported_defaults_to_en(self):
        assert map_telegram_language("ja") == "en"
        assert map_telegram_language("ko") == "en"

    def test_case_insensitive(self):
        assert map_telegram_language("RU") == "ru"
        assert map_telegram_language("De") == "de"

    def test_with_region_suffix(self):
        assert map_telegram_language("ru-RU") == "ru"
        assert map_telegram_language("de-AT") == "de"
        assert map_telegram_language("en-US") == "en"


class TestParseDate:
    def test_dot_format(self):
        assert parse_date("15.03.1990") == date(1990, 3, 15)

    def test_slash_format(self):
        assert parse_date("15/03/1990") == date(1990, 3, 15)

    def test_dash_format(self):
        assert parse_date("15-03-1990") == date(1990, 3, 15)

    def test_iso_format(self):
        assert parse_date("1990-03-15") == date(1990, 3, 15)

    def test_iso_slash_format(self):
        assert parse_date("1990/03/15") == date(1990, 3, 15)

    def test_iso_dot_format(self):
        assert parse_date("1990.03.15") == date(1990, 3, 15)

    def test_invalid_returns_none(self):
        assert parse_date("not-a-date") is None

    def test_empty_returns_none(self):
        assert parse_date("") is None

    def test_whitespace_stripped(self):
        assert parse_date("  15.03.1990  ") == date(1990, 3, 15)

    def test_partial_date_returns_none(self):
        assert parse_date("15.03") is None


class TestTranslationCompleteness:
    """Verify all message constants have all language translations."""

    def test_all_messages_have_all_languages(self):
        for msg in _ALL_MESSAGE_CONSTANTS:
            msgid = str(msg)
            for lang in settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES:
                result = translate(msg, lang)
                assert result, (
                    f"Message '{msgid[:50]}...' has empty translation for '{lang}'"
                )

    def test_language_names_complete(self):
        for lang in settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES:
            assert lang in settings.HOROSCOPE_LANGUAGE_NAMES

    def test_language_flags_complete(self):
        for lang in settings.HOROSCOPE_SUPPORTED_LANGUAGE_CODES:
            assert lang in settings.HOROSCOPE_LANGUAGE_FLAGS


class TestBackgroundTasks:
    """Tests for background tasks with mocked dependencies."""

    @pytest.mark.django_db
    async def test_generate_horoscope_success(self):
        from horoscope.tasks.generate_horoscope import generate_horoscope

        mock_horoscope = MagicMock()
        mock_horoscope.id = 42
        mock_horoscope.full_text = "Your horoscope text"
        mock_horoscope.teaser_text = "Teaser text"
        mock_horoscope.extended_teaser_text = "Extended teaser text"

        mock_service = MagicMock()
        mock_service.agenerate_for_user = AsyncMock(return_value=mock_horoscope)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.generate_horoscope._send_daily_horoscope',
            new_callable=AsyncMock,
        ) as mock_send:
            mock_container.horoscope.horoscope_service.return_value = mock_service

            await generate_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
                horoscope_type="daily",
            )

        mock_service.agenerate_for_user.assert_called_once_with(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
            horoscope_type="daily",
        )
        mock_send.assert_called_once_with(
            bot=mock_bot,
            telegram_uid=12345,
            horoscope_id=42,
            full_text="Your horoscope text",
            teaser_text="Teaser text",
            extended_teaser_text="Extended teaser text",
        )

    @pytest.mark.django_db
    async def test_generate_horoscope_value_error(self):
        from horoscope.tasks.generate_horoscope import generate_horoscope

        mock_service = MagicMock()
        mock_service.agenerate_for_user = AsyncMock(side_effect=ValueError("No profile"))

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container:
            mock_container.horoscope.horoscope_service.return_value = mock_service

            with pytest.raises(ValueError, match="No profile"):
                await generate_horoscope(
                    bot=mock_bot,
                    telegram_uid=12345,
                    target_date="2024-06-15",
                )

    @pytest.mark.django_db
    async def test_generate_horoscope_first_sends_message(self):
        from horoscope.tasks.generate_horoscope import generate_horoscope

        mock_horoscope = MagicMock()
        mock_horoscope.id = 42
        mock_horoscope.full_text = "First horoscope"

        mock_service = MagicMock()
        mock_service.agenerate_for_user = AsyncMock(return_value=mock_horoscope)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.generate_horoscope._send_first_horoscope',
            new_callable=AsyncMock,
        ) as mock_send:
            mock_container.horoscope.horoscope_service.return_value = mock_service

            await generate_horoscope(
                bot=mock_bot,
                telegram_uid=12345,
                target_date="2024-06-15",
                horoscope_type="first",
            )

        mock_send.assert_called_once_with(
            bot=mock_bot,
            telegram_uid=12345,
            horoscope_id=42,
            full_text="First horoscope",
        )

    @pytest.mark.django_db
    async def test_generate_daily_for_all_users(self):
        from horoscope.tasks.send_daily_horoscope import generate_daily_for_all_users

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_all_telegram_uids = AsyncMock(return_value=[111, 222, 333])

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.generate_horoscope.generate_horoscope',
            new_callable=AsyncMock,
        ) as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = await generate_daily_for_all_users(mock_bot)

        assert result == 3
        assert mock_task.call_count == 3

    @pytest.mark.django_db
    async def test_send_daily_horoscope_notifications(self):
        from horoscope.entities import HoroscopeEntity, UserProfileEntity
        from horoscope.tasks.send_daily_horoscope import send_daily_horoscope_notifications

        profile = UserProfileEntity(
            user_telegram_uid=12345,
            name="Test",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="en",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        horoscope = HoroscopeEntity(
            id=1,
            user_telegram_uid=12345,
            horoscope_type="daily",
            date=date.today(),
            full_text="Full text",
            teaser_text="Teaser",
            created_at=datetime(2024, 1, 1),
        )

        mock_profile_repo = MagicMock()
        mock_profile_repo.aall = AsyncMock(return_value=[profile])

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
        mock_horoscope_repo.amark_sent = AsyncMock()

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_message',
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = await send_daily_horoscope_notifications(mock_bot)

        assert result == 1
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs['telegram_uid'] == 12345
        assert "Full text" in call_kwargs['text']
        assert "just type your message" in call_kwargs['text']
        mock_horoscope_repo.amark_sent.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    async def test_send_daily_horoscope_non_subscriber_skipped(self):
        """Non-subscribers are skipped by daily notification task (they get periodic teasers instead)."""
        from horoscope.entities import UserProfileEntity
        from horoscope.tasks.send_daily_horoscope import send_daily_horoscope_notifications

        profile = UserProfileEntity(
            user_telegram_uid=12345,
            name="Test",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="en",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

        mock_profile_repo = MagicMock()
        mock_profile_repo.aall = AsyncMock(return_value=[profile])

        mock_horoscope_repo = MagicMock()

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=False)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_message',
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = await send_daily_horoscope_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()
        mock_horoscope_repo.aget_by_user_and_date.assert_not_called()

    @pytest.mark.django_db
    async def test_send_daily_horoscope_skips_already_sent(self):
        """Horoscopes that already have sent_at set should not be sent again."""
        from horoscope.entities import HoroscopeEntity, UserProfileEntity
        from horoscope.tasks.send_daily_horoscope import send_daily_horoscope_notifications

        profile = UserProfileEntity(
            user_telegram_uid=12345,
            name="Test",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="en",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        horoscope = HoroscopeEntity(
            id=1,
            user_telegram_uid=12345,
            horoscope_type="daily",
            date=date.today(),
            full_text="Full text",
            teaser_text="Teaser",
            sent_at=timezone.now(),
            created_at=datetime(2024, 1, 1),
        )

        mock_profile_repo = MagicMock()
        mock_profile_repo.aall = AsyncMock(return_value=[profile])

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.ahas_active_subscription = AsyncMock(return_value=True)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_message',
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = await send_daily_horoscope_notifications(mock_bot)

        assert result == 0
        mock_send.assert_not_called()

    @pytest.mark.django_db
    async def test_send_expiry_reminders_no_expiring(self):
        from horoscope.tasks.subscription_reminders import send_expiry_reminders

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.aget_expiring_soon = AsyncMock(return_value=[])

        mock_profile_repo = MagicMock()

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            result = await send_expiry_reminders(mock_bot)

        assert result == 0

    @pytest.mark.django_db
    async def test_send_expiry_reminders_with_expiring(self):
        from horoscope.entities import SubscriptionEntity, UserProfileEntity
        from horoscope.tasks.subscription_reminders import send_expiry_reminders

        now = timezone.now()
        sub = SubscriptionEntity(
            id=1,
            user_telegram_uid=12345,
            status="active",
            started_at=datetime(2024, 1, 1),
            expires_at=now + timedelta(days=2),
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        profile = UserProfileEntity(
            user_telegram_uid=12345,
            name="Test",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="en",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.aget_expiring_soon = AsyncMock(return_value=[sub])
        mock_subscription_repo.amark_reminded = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_messages_batch',
            new_callable=AsyncMock,
            return_value=1,
        ) as mock_send:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            result = await send_expiry_reminders(mock_bot)

        assert result == 1
        mock_send.assert_called_once()
        mock_subscription_repo.amark_reminded.assert_called_once_with(
            subscription_ids=[1],
        )

    @pytest.mark.django_db
    async def test_send_expired_notifications_no_expired(self):
        from horoscope.tasks.subscription_reminders import send_expired_notifications

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.aget_recently_expired_unnotified = AsyncMock(return_value=[])

        mock_profile_repo = MagicMock()

        mock_service = MagicMock()
        mock_service.aexpire_overdue_subscriptions = AsyncMock()

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_service.return_value = mock_service

            result = await send_expired_notifications(mock_bot)

        assert result == 0
        mock_service.aexpire_overdue_subscriptions.assert_called_once()

    @pytest.mark.django_db
    async def test_send_expired_notifications_with_expired(self):
        from horoscope.entities import SubscriptionEntity, UserProfileEntity
        from horoscope.tasks.subscription_reminders import send_expired_notifications

        now = timezone.now()
        sub = SubscriptionEntity(
            id=1,
            user_telegram_uid=12345,
            status="expired",
            started_at=datetime(2024, 1, 1),
            expires_at=now - timedelta(days=1),
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        profile = UserProfileEntity(
            user_telegram_uid=12345,
            name="Test",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="ru",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.aget_recently_expired_unnotified = AsyncMock(return_value=[sub])
        mock_subscription_repo.amark_reminded = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)

        mock_service = MagicMock()
        mock_service.aexpire_overdue_subscriptions = AsyncMock()

        mock_bot = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_messages_batch',
            new_callable=AsyncMock,
            return_value=1,
        ) as mock_send:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_service.return_value = mock_service

            result = await send_expired_notifications(mock_bot)

        assert result == 1
        mock_send.assert_called_once()
        mock_subscription_repo.amark_reminded.assert_called_once_with(
            subscription_ids=[1],
        )


class TestLLMService:
    """Tests for the LLM service with mocked litellm."""

    def test_is_configured_true(self):
        from horoscope.services.llm import LLMService

        with patch('horoscope.services.llm.settings') as mock_settings:
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.LLM_BASE_URL = None
            mock_settings.LLM_TIMEOUT = 30

            service = LLMService()
            assert service.is_configured is True

    def test_is_configured_false(self):
        from horoscope.services.llm import LLMService

        with patch('horoscope.services.llm.settings') as mock_settings:
            mock_settings.LLM_API_KEY = ""
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.LLM_BASE_URL = None
            mock_settings.LLM_TIMEOUT = 30

            service = LLMService()
            assert service.is_configured is False

    def test_generate_horoscope_text(self):
        from horoscope.services.llm import LLMService

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Horoscope for Taurus\n"
            "Dear Alice,\n"
            "\n"
            "Line 1\n"
            "Line 2\n"
            "Line 3\n"
            "Line 4\n"
            "Line 5"
        )
        mock_response.model = "gpt-4"
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 250

        with patch('horoscope.services.llm.settings') as mock_settings, \
             patch('litellm.completion', return_value=mock_response) as mock_llm:
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.LLM_BASE_URL = None
            mock_settings.LLM_TIMEOUT = 30
            mock_settings.HOROSCOPE_TEASER_LINE_COUNT = 3

            service = LLMService()
            result = service.generate_horoscope_text(
                zodiac_sign="Taurus",
                name="Alice",
                date_of_birth=date(1990, 5, 15),
                place_of_birth="London",
                place_of_living="Berlin",
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert "Horoscope for Taurus" in result.full_text
        assert "..." in result.teaser_text
        assert result.model == "gpt-4"
        assert result.input_tokens == 150
        assert result.output_tokens == 250
        mock_llm.assert_called_once()

    def test_generate_horoscope_text_with_language(self):
        from horoscope.services.llm import LLMService

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Гороскоп для Тельца"

        with patch('horoscope.services.llm.settings') as mock_settings, \
             patch('litellm.completion', return_value=mock_response) as mock_llm:
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.LLM_BASE_URL = None
            mock_settings.LLM_TIMEOUT = 30
            mock_settings.HOROSCOPE_TEASER_LINE_COUNT = 3
            mock_settings.HOROSCOPE_LANGUAGE_NAMES = settings.HOROSCOPE_LANGUAGE_NAMES

            service = LLMService()
            service.generate_horoscope_text(
                zodiac_sign="Taurus",
                name="Алиса",
                date_of_birth=date(1990, 5, 15),
                place_of_birth="Moscow",
                place_of_living="Berlin",
                target_date=date(2024, 6, 15),
                language="ru",
            )

        call_args = mock_llm.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert "Русский" in prompt
