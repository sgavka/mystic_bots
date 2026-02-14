"""
Tests for the translation system and Celery tasks.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from horoscope.messages import (
    LANGUAGE_FLAGS,
    LANGUAGE_NAMES,
    SUBSCRIPTION_OFFER,
    SUPPORTED_LANGUAGE_CODES,
    TASK_EXPIRY_REMINDER,
    WIZARD_WELCOME,
    WIZARD_WELCOME_BACK,
    map_telegram_language,
    translate,
)

# All message constants for completeness tests
from horoscope import messages as _msg

_ALL_MESSAGE_CONSTANTS = [
    _msg.WIZARD_CHOOSE_LANGUAGE, _msg.WIZARD_WELCOME_BACK, _msg.WIZARD_WELCOME,
    _msg.WIZARD_INVALID_NAME, _msg.WIZARD_ASK_DOB, _msg.WIZARD_INVALID_DATE_FORMAT,
    _msg.WIZARD_DOB_IN_FUTURE, _msg.WIZARD_DOB_TOO_OLD, _msg.WIZARD_ASK_PLACE_OF_BIRTH,
    _msg.WIZARD_INVALID_CITY, _msg.WIZARD_ASK_PLACE_OF_LIVING, _msg.WIZARD_PROFILE_READY,
    _msg.HOROSCOPE_NO_PROFILE, _msg.HOROSCOPE_NOT_READY, _msg.HOROSCOPE_GENERATING,
    _msg.HOROSCOPE_SUBSCRIBE_CTA, _msg.SUBSCRIPTION_OFFER, _msg.SUBSCRIPTION_INVOICE_TITLE,
    _msg.SUBSCRIPTION_INVOICE_DESCRIPTION, _msg.SUBSCRIPTION_PAYMENT_SUCCESS,
    _msg.KEYBOARD_SUBSCRIBE, _msg.TASK_FIRST_HOROSCOPE_READY, _msg.TASK_EXPIRY_REMINDER,
    _msg.TASK_SUBSCRIPTION_EXPIRED, _msg.LANGUAGE_CURRENT, _msg.LANGUAGE_CHANGED,
    _msg.LANGUAGE_NO_PROFILE, _msg.HOROSCOPE_HEADER, _msg.HOROSCOPE_GREETING,
    _msg.ERROR_PROFILE_CREATION_FAILED, _msg.ERROR_PAYMENT_FAILED,
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

    def test_unsupported_language_falls_back_to_en(self):
        result = translate(WIZARD_WELCOME, "fr")
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

    def test_english(self):
        assert map_telegram_language("en") == "en"

    def test_none_defaults_to_en(self):
        assert map_telegram_language(None) == "en"

    def test_unsupported_defaults_to_en(self):
        assert map_telegram_language("fr") == "en"
        assert map_telegram_language("ja") == "en"

    def test_case_insensitive(self):
        assert map_telegram_language("RU") == "ru"
        assert map_telegram_language("De") == "de"

    def test_with_region_suffix(self):
        assert map_telegram_language("ru-RU") == "ru"
        assert map_telegram_language("de-AT") == "de"
        assert map_telegram_language("en-US") == "en"


class TestTranslationCompleteness:
    """Verify all message constants have all 4 language translations."""

    def test_all_messages_have_all_languages(self):
        for msg in _ALL_MESSAGE_CONSTANTS:
            msgid = str(msg)
            for lang in SUPPORTED_LANGUAGE_CODES:
                result = translate(msg, lang)
                assert result, (
                    f"Message '{msgid[:50]}...' has empty translation for '{lang}'"
                )

    def test_language_names_complete(self):
        for lang in SUPPORTED_LANGUAGE_CODES:
            assert lang in LANGUAGE_NAMES

    def test_language_flags_complete(self):
        for lang in SUPPORTED_LANGUAGE_CODES:
            assert lang in LANGUAGE_FLAGS


class TestCeleryTasks:
    """Tests for Celery tasks with mocked dependencies."""

    @pytest.mark.django_db
    def test_generate_horoscope_task_success(self):
        from horoscope.tasks.generate_horoscope import generate_horoscope_task

        mock_horoscope = MagicMock()
        mock_horoscope.id = 42
        mock_horoscope.full_text = "Your horoscope text"
        mock_horoscope.teaser_text = "Teaser text"

        mock_service = MagicMock()
        mock_service.generate_for_user.return_value = mock_horoscope

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.generate_horoscope._send_daily_horoscope',
        ) as mock_send:
            mock_container.horoscope.horoscope_service.return_value = mock_service

            result = generate_horoscope_task(
                telegram_uid=12345,
                target_date="2024-06-15",
                horoscope_type="daily",
            )

        assert result == 42
        mock_service.generate_for_user.assert_called_once_with(
            telegram_uid=12345,
            target_date=date(2024, 6, 15),
            horoscope_type="daily",
        )
        mock_send.assert_called_once_with(
            telegram_uid=12345,
            horoscope_id=42,
            full_text="Your horoscope text",
            teaser_text="Teaser text",
        )

    @pytest.mark.django_db
    def test_generate_horoscope_task_value_error(self):
        from horoscope.tasks.generate_horoscope import generate_horoscope_task

        mock_service = MagicMock()
        mock_service.generate_for_user.side_effect = ValueError("No profile")

        with patch(
            'core.containers.container'
        ) as mock_container:
            mock_container.horoscope.horoscope_service.return_value = mock_service

            result = generate_horoscope_task(
                telegram_uid=12345,
                target_date="2024-06-15",
            )

        assert result is None

    @pytest.mark.django_db
    def test_generate_horoscope_task_first_sends_message(self):
        from horoscope.tasks.generate_horoscope import generate_horoscope_task

        mock_horoscope = MagicMock()
        mock_horoscope.id = 42
        mock_horoscope.full_text = "First horoscope"

        mock_service = MagicMock()
        mock_service.generate_for_user.return_value = mock_horoscope

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.generate_horoscope._send_first_horoscope',
        ) as mock_send:
            mock_container.horoscope.horoscope_service.return_value = mock_service

            result = generate_horoscope_task(
                telegram_uid=12345,
                target_date="2024-06-15",
                horoscope_type="first",
            )

        assert result == 42
        mock_send.assert_called_once_with(
            telegram_uid=12345,
            horoscope_id=42,
            full_text="First horoscope",
        )

    @pytest.mark.django_db
    def test_generate_daily_for_all_users_task(self):
        from horoscope.tasks.send_daily_horoscope import (
            generate_daily_for_all_users_task,
        )

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_all_telegram_uids.return_value = [111, 222, 333]

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.generate_horoscope.generate_horoscope_task'
        ) as mock_task:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            result = generate_daily_for_all_users_task()

        assert result == 3
        assert mock_task.delay.call_count == 3

    @pytest.mark.django_db
    def test_send_daily_horoscope_notifications_task(self):
        from horoscope.entities import HoroscopeEntity, UserProfileEntity
        from horoscope.tasks.send_daily_horoscope import (
            send_daily_horoscope_notifications_task,
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
        mock_profile_repo.all.return_value = [profile]

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.get_by_user_and_date.return_value = horoscope

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = True

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_message',
            return_value=True,
        ) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = send_daily_horoscope_notifications_task()

        assert result == 1
        mock_send.assert_called_once_with(
            telegram_uid=12345,
            text="Full text",
            reply_markup=None,
        )
        mock_horoscope_repo.mark_sent.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    def test_send_daily_horoscope_non_subscriber_gets_teaser(self):
        from horoscope.entities import HoroscopeEntity, UserProfileEntity
        from horoscope.tasks.send_daily_horoscope import (
            send_daily_horoscope_notifications_task,
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
        mock_profile_repo.all.return_value = [profile]

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.get_by_user_and_date.return_value = horoscope

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.has_active_subscription.return_value = False

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_message',
            return_value=True,
        ) as mock_send:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo

            result = send_daily_horoscope_notifications_task()

        assert result == 1
        text = mock_send.call_args[1]['text']
        assert "Teaser" in text
        assert "Subscribe" in text or "🔒" in text
        mock_horoscope_repo.mark_sent.assert_called_once_with(horoscope_id=1)

    @pytest.mark.django_db
    def test_send_expiry_reminders_task_no_expiring(self):
        from horoscope.tasks.subscription_reminders import send_expiry_reminders_task

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_expiring_soon.return_value = []

        mock_profile_repo = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            result = send_expiry_reminders_task()

        assert result == 0

    @pytest.mark.django_db
    def test_send_expiry_reminders_task_with_expiring(self):
        from horoscope.entities import SubscriptionEntity, UserProfileEntity
        from horoscope.tasks.subscription_reminders import send_expiry_reminders_task

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
        mock_subscription_repo.get_expiring_soon.return_value = [sub]

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_telegram_uid.return_value = profile

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_messages_batch',
            return_value=1,
        ) as mock_send:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            result = send_expiry_reminders_task()

        assert result == 1
        mock_send.assert_called_once()
        mock_subscription_repo.mark_reminded.assert_called_once_with(
            subscription_ids=[1],
        )

    @pytest.mark.django_db
    def test_send_expired_notifications_task_no_expired(self):
        from horoscope.tasks.subscription_reminders import (
            send_expired_notifications_task,
        )

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_recently_expired_unnotified.return_value = []

        mock_profile_repo = MagicMock()

        mock_service = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_service.return_value = mock_service

            result = send_expired_notifications_task()

        assert result == 0
        mock_service.expire_overdue_subscriptions.assert_called_once()

    @pytest.mark.django_db
    def test_send_expired_notifications_task_with_expired(self):
        from horoscope.entities import SubscriptionEntity, UserProfileEntity
        from horoscope.tasks.subscription_reminders import (
            send_expired_notifications_task,
        )

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
        mock_subscription_repo.get_recently_expired_unnotified.return_value = [sub]

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_telegram_uid.return_value = profile

        mock_service = MagicMock()

        with patch(
            'core.containers.container'
        ) as mock_container, patch(
            'horoscope.tasks.messaging.send_messages_batch',
            return_value=1,
        ) as mock_send:
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_service.return_value = mock_service

            result = send_expired_notifications_task()

        assert result == 1
        mock_send.assert_called_once()
        mock_subscription_repo.mark_reminded.assert_called_once_with(
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

        with patch('horoscope.services.llm.settings') as mock_settings, \
             patch('litellm.completion', return_value=mock_response) as mock_llm:
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.LLM_BASE_URL = None
            mock_settings.LLM_TIMEOUT = 30
            mock_settings.HOROSCOPE_TEASER_LINE_COUNT = 3

            service = LLMService()
            full_text, teaser_text = service.generate_horoscope_text(
                zodiac_sign="Taurus",
                name="Alice",
                date_of_birth=date(1990, 5, 15),
                place_of_birth="London",
                place_of_living="Berlin",
                target_date=date(2024, 6, 15),
                language="en",
            )

        assert "Horoscope for Taurus" in full_text
        assert "..." in teaser_text
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
