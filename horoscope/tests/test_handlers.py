"""
Tests for horoscope bot handlers using aiogram-test-framework.
Covers all user flows: wizard onboarding, horoscope view, subscription, language.
"""

import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram import BaseMiddleware, Bot, Dispatcher
from dependency_injector import providers

from aiogram_test_framework import TestClient

from core.containers import container
from core.entities import UserEntity
from core.enums import BotSlug
from horoscope.entities import HoroscopeEntity, UserProfileEntity


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

class _MockUserMiddleware(BaseMiddleware):
    """Injects UserEntity from the Telegram user, bypassing real DB."""

    async def __call__(self, handler, event, data):
        from_user = getattr(event, 'from_user', None)
        if from_user:
            data['user'] = UserEntity(
                telegram_uid=from_user.id,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
                username=from_user.username,
                language_code=from_user.language_code or 'en',
                is_premium=from_user.is_premium or False,
            )
        data['bot_slug'] = BotSlug.HOROSCOPE
        return await handler(event, data)


def _setup_dispatcher(bot: Bot, dispatcher: Dispatcher) -> None:
    middleware = _MockUserMiddleware()
    dispatcher.message.middleware(middleware)
    dispatcher.callback_query.middleware(middleware)

    from horoscope.handlers.wizard import router as wizard_router
    from horoscope.handlers.horoscope import router as horoscope_router
    from horoscope.handlers.subscription import router as subscription_router
    from horoscope.handlers.language import router as language_router

    dispatcher.include_router(wizard_router)
    dispatcher.include_router(horoscope_router)
    dispatcher.include_router(subscription_router)
    dispatcher.include_router(language_router)


def _make_profile(
    telegram_uid: int = 100000,
    name: str = "Test User",
    date_of_birth: date = date(1990, 5, 15),
    place_of_birth: str = "London",
    place_of_living: str = "Berlin",
    preferred_language: str = "en",
) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name=name,
        date_of_birth=date_of_birth,
        place_of_birth=place_of_birth,
        place_of_living=place_of_living,
        preferred_language=preferred_language,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


def _make_horoscope(
    telegram_uid: int = 100000,
    full_text: str = "Your full horoscope text here.",
    teaser_text: str = "Your teaser...",
) -> HoroscopeEntity:
    return HoroscopeEntity(
        id=1,
        user_telegram_uid=telegram_uid,
        horoscope_type="daily",
        date=date.today(),
        full_text=full_text,
        teaser_text=teaser_text,
        created_at=datetime(2024, 1, 1),
    )


def _mock_profile_repo(profile=None):
    mock = MagicMock()
    mock.aget_by_telegram_uid = AsyncMock(return_value=profile)
    mock.get_by_telegram_uid = MagicMock(return_value=profile)
    mock.create_profile = MagicMock(return_value=profile)
    mock.update_language = MagicMock(return_value=profile)
    mock.aupdate_language = AsyncMock(return_value=profile)
    return mock


def _mock_horoscope_repo(horoscope=None):
    mock = MagicMock()
    mock.aget_by_user_and_date = AsyncMock(return_value=horoscope)
    mock.get_by_user_and_date = MagicMock(return_value=horoscope)
    return mock


def _mock_subscription_repo(has_active: bool = False):
    mock = MagicMock()
    mock.has_active_subscription = MagicMock(return_value=has_active)
    mock.ahas_active_subscription = AsyncMock(return_value=has_active)
    return mock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def client():
    c = await TestClient.create(
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        bot_id=123456,
        bot_username="test_bot",
        bot_first_name="Test Bot",
        setup_dispatcher_func=_setup_dispatcher,
    )
    yield c
    await c.close()


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    for prov in [
        container.horoscope.user_profile_repository,
        container.horoscope.horoscope_repository,
        container.horoscope.subscription_repository,
    ]:
        try:
            prov.reset_override()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Helper: complete language selection step in wizard
# ---------------------------------------------------------------------------

async def _select_language(user, lang_code: str = "en"):
    """Click a language button during wizard language selection step."""
    responses = await user.click_button(f"lang_{lang_code}")
    return responses


# ---------------------------------------------------------------------------
# Wizard: /start → language selection
# ---------------------------------------------------------------------------

class TestWizardStart:

    async def test_start_new_user_shows_language_selection(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        responses = await user.send_command("start")

        assert len(responses) == 1
        assert "language" in responses[0].text.lower() or "🌍" in responses[0].text

    async def test_start_returning_user(self, client):
        profile = _make_profile(name="Alice")
        profile_repo = _mock_profile_repo(profile=profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="Alice")
        responses = await user.send_command("start")

        assert len(responses) == 1
        assert "Alice" in responses[0].text

    async def test_start_returning_user_russian(self, client):
        profile = _make_profile(name="Алиса", preferred_language="ru")
        profile_repo = _mock_profile_repo(profile=profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="Алиса")
        responses = await user.send_command("start")

        assert len(responses) == 1
        assert "Алиса" in responses[0].text


# ---------------------------------------------------------------------------
# Wizard: language → name step
# ---------------------------------------------------------------------------

class TestWizardLanguageToName:

    async def _start_wizard_and_pick_language(self, client, lang_code: str = "en"):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        user = client.create_user(first_name="John")
        await user.send_command("start")
        await _select_language(user, lang_code)
        return user

    async def test_language_en_then_welcome(self, client):
        await self._start_wizard_and_pick_language(client, "en")

        # After picking language, the bot should send the welcome message
        sent = client.capture.get_sent_messages()
        last_text = sent[-1].text if sent else ""
        assert "name" in last_text.lower() or "Mystic Horoscope" in last_text

    async def test_language_ru_then_welcome_in_russian(self, client):
        await self._start_wizard_and_pick_language(client, "ru")

        sent = client.capture.get_sent_messages()
        last_text = sent[-1].text if sent else ""
        assert "Mystic Horoscope" in last_text or "зовут" in last_text.lower()


# ---------------------------------------------------------------------------
# Wizard: name step
# ---------------------------------------------------------------------------

class TestWizardName:

    async def _enter_wizard(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        user = client.create_user(first_name="John")
        await user.send_command("start")
        await _select_language(user, "en")
        return user

    async def test_valid_name(self, client):
        user = await self._enter_wizard(client)
        responses = await user.send_message("Alice")

        assert len(responses) == 1
        assert "Alice" in responses[0].text
        assert "date of birth" in responses[0].text.lower()

    async def test_name_too_short(self, client):
        user = await self._enter_wizard(client)
        responses = await user.send_message("A")

        assert len(responses) == 1
        assert "valid name" in responses[0].text.lower() or "2-100" in responses[0].text

    async def test_name_too_long(self, client):
        user = await self._enter_wizard(client)
        responses = await user.send_message("A" * 101)

        assert len(responses) == 1
        assert "valid name" in responses[0].text.lower() or "2-100" in responses[0].text


# ---------------------------------------------------------------------------
# Wizard: date of birth step
# ---------------------------------------------------------------------------

class TestWizardDateOfBirth:

    async def _enter_dob_step(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        user = client.create_user(first_name="John")
        await user.send_command("start")
        await _select_language(user, "en")
        await user.send_message("Alice")
        return user

    async def test_valid_date(self, client):
        user = await self._enter_dob_step(client)
        responses = await user.send_message("15.03.1990")

        assert len(responses) == 1
        assert "place of birth" in responses[0].text.lower()

    async def test_invalid_format(self, client):
        user = await self._enter_dob_step(client)
        responses = await user.send_message("1990-03-15")

        assert len(responses) == 1
        assert "DD.MM.YYYY" in responses[0].text

    async def test_future_date(self, client):
        user = await self._enter_dob_step(client)
        responses = await user.send_message("15.03.2099")

        assert len(responses) == 1
        assert "past" in responses[0].text.lower()

    async def test_too_old_date(self, client):
        user = await self._enter_dob_step(client)
        responses = await user.send_message("01.01.1800")

        assert len(responses) == 1
        assert "valid date" in responses[0].text.lower()


# ---------------------------------------------------------------------------
# Wizard: place of birth step
# ---------------------------------------------------------------------------

class TestWizardPlaceOfBirth:

    async def _enter_pob_step(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        user = client.create_user(first_name="John")
        await user.send_command("start")
        await _select_language(user, "en")
        await user.send_message("Alice")
        await user.send_message("15.03.1990")
        return user

    async def test_valid_place(self, client):
        user = await self._enter_pob_step(client)
        responses = await user.send_message("London")

        assert len(responses) == 1
        assert "place of living" in responses[0].text.lower() or "living" in responses[0].text.lower()

    async def test_place_too_short(self, client):
        user = await self._enter_pob_step(client)
        responses = await user.send_message("A")

        assert len(responses) == 1
        assert "valid city" in responses[0].text.lower() or "2-200" in responses[0].text


# ---------------------------------------------------------------------------
# Wizard: place of living + profile creation
# ---------------------------------------------------------------------------

class TestWizardPlaceOfLiving:

    async def _enter_pol_step(self, client):
        created_profile = _make_profile(
            name="Alice",
            date_of_birth=date(1990, 3, 15),
            place_of_birth="London",
            place_of_living="Berlin",
        )
        profile_repo = _mock_profile_repo(profile=None)
        profile_repo.create_profile = MagicMock(return_value=created_profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        await user.send_command("start")
        await _select_language(user, "en")
        await user.send_message("Alice")
        await user.send_message("15.03.1990")
        await user.send_message("London")
        return user, profile_repo

    async def test_valid_place_creates_profile(self, client):
        user, profile_repo = await self._enter_pol_step(client)

        with patch('horoscope.tasks.generate_horoscope_task') as mock_task:
            responses = await user.send_message("Berlin")

            assert len(responses) == 1
            assert "profile is ready" in responses[0].text.lower()
            assert "Alice" in responses[0].text
            profile_repo.create_profile.assert_called_once()
            mock_task.delay.assert_called_once()

    async def test_place_too_short(self, client):
        user, _ = await self._enter_pol_step(client)
        responses = await user.send_message("A")

        assert len(responses) == 1
        assert "valid city" in responses[0].text.lower() or "2-200" in responses[0].text


# ---------------------------------------------------------------------------
# Wizard: complete flow (happy path)
# ---------------------------------------------------------------------------

class TestWizardFullFlow:

    async def test_complete_wizard(self, client):
        created_profile = _make_profile(
            name="Alice",
            date_of_birth=date(1990, 3, 15),
            place_of_birth="London",
            place_of_living="Berlin",
        )
        profile_repo = _mock_profile_repo(profile=None)
        profile_repo.create_profile = MagicMock(return_value=created_profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")

        # Step 1: /start → language selection
        responses = await user.send_command("start")
        assert "🌍" in responses[0].text or "language" in responses[0].text.lower()

        # Step 2: select language
        await _select_language(user, "en")

        # Step 3: name
        responses = await user.send_message("Alice")
        assert "Alice" in responses[0].text
        assert "date of birth" in responses[0].text.lower()

        # Step 4: date of birth
        responses = await user.send_message("15.03.1990")
        assert "place of birth" in responses[0].text.lower()

        # Step 5: place of birth
        responses = await user.send_message("London")
        assert "place of living" in responses[0].text.lower() or "living" in responses[0].text.lower()

        # Step 6: place of living → profile created, horoscope queued
        with patch('horoscope.tasks.generate_horoscope_task') as mock_task:
            responses = await user.send_message("Berlin")

            assert "profile is ready" in responses[0].text.lower()
            assert "Alice" in responses[0].text
            assert "15.03.1990" in responses[0].text
            assert "London" in responses[0].text
            assert "Berlin" in responses[0].text
            mock_task.delay.assert_called_once()


# ---------------------------------------------------------------------------
# Horoscope view handler
# ---------------------------------------------------------------------------

class TestHoroscopeView:

    async def test_no_profile(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        responses = await user.send_command("horoscope")

        assert len(responses) == 1
        assert "profile" in responses[0].text.lower()
        assert "/start" in responses[0].text

    async def test_no_horoscope_today(self, client):
        profile_repo = _mock_profile_repo(profile=_make_profile())
        horoscope_repo = _mock_horoscope_repo(horoscope=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        container.horoscope.horoscope_repository.override(
            providers.Object(horoscope_repo)
        )

        user = client.create_user(first_name="Test")
        responses = await user.send_command("horoscope")

        assert len(responses) == 1
        assert "not ready" in responses[0].text.lower()

    async def test_subscriber_sees_full_text(self, client):
        full_text = "Full horoscope for today."
        horoscope = _make_horoscope(full_text=full_text)

        profile_repo = _mock_profile_repo(profile=_make_profile())
        horoscope_repo = _mock_horoscope_repo(horoscope=horoscope)
        subscription_repo = _mock_subscription_repo(has_active=True)

        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        container.horoscope.horoscope_repository.override(
            providers.Object(horoscope_repo)
        )
        container.horoscope.subscription_repository.override(
            providers.Object(subscription_repo)
        )

        user = client.create_user(first_name="Test")
        responses = await user.send_command("horoscope")

        assert len(responses) == 1
        assert responses[0].text == full_text

    async def test_non_subscriber_sees_teaser(self, client):
        teaser = "Teaser preview..."
        horoscope = _make_horoscope(teaser_text=teaser)

        profile_repo = _mock_profile_repo(profile=_make_profile())
        horoscope_repo = _mock_horoscope_repo(horoscope=horoscope)
        subscription_repo = _mock_subscription_repo(has_active=False)

        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )
        container.horoscope.horoscope_repository.override(
            providers.Object(horoscope_repo)
        )
        container.horoscope.subscription_repository.override(
            providers.Object(subscription_repo)
        )

        user = client.create_user(first_name="Test")
        responses = await user.send_command("horoscope")

        assert len(responses) == 1
        assert teaser in responses[0].text
        assert "subscribe" in responses[0].text.lower() or "🔒" in responses[0].text


# ---------------------------------------------------------------------------
# Subscription handler
# ---------------------------------------------------------------------------

class TestSubscription:

    async def test_subscribe_callback(self, client):
        # Set up a profile so language lookup works
        profile_repo = _mock_profile_repo(profile=_make_profile())
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        await user.click_button("subscribe")

        # Handler calls callback.answer() and then sends messages
        callback_answers = client.capture.get_callback_answers()
        assert len(callback_answers) >= 1

        sent_messages = client.capture.get_sent_messages()
        has_subscribe_info = any(
            "subscribe" in (m.text or "").lower() or "⭐" in (m.text or "")
            for m in sent_messages
        )
        assert has_subscribe_info


# ---------------------------------------------------------------------------
# Language command handler
# ---------------------------------------------------------------------------

class TestLanguageCommand:

    async def test_language_command_shows_current(self, client):
        profile = _make_profile(preferred_language="en")
        profile_repo = _mock_profile_repo(profile=profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        responses = await user.send_command("language")

        assert len(responses) == 1
        assert "language" in responses[0].text.lower() or "🌍" in responses[0].text

    async def test_language_command_no_profile(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        responses = await user.send_command("language")

        assert len(responses) == 1
        assert "profile" in responses[0].text.lower() or "/start" in responses[0].text

    async def test_change_language(self, client):
        profile = _make_profile(preferred_language="en")
        updated_profile = _make_profile(preferred_language="ru")
        profile_repo = _mock_profile_repo(profile=profile)
        profile_repo.update_language = MagicMock(return_value=updated_profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        # First send /language to get the keyboard
        await user.send_command("language")

        # Then click on Russian
        await user.click_button("lang_ru")

        callback_answers = client.capture.get_callback_answers()
        assert len(callback_answers) >= 1

        sent_messages = client.capture.get_sent_messages()
        has_language_changed = any(
            "Русский" in (m.text or "") or "language" in (m.text or "").lower()
            for m in sent_messages
        )
        assert has_language_changed


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------

class TestErrorHandling:

    async def test_wizard_profile_creation_failure(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        profile_repo.create_profile = MagicMock(side_effect=Exception("DB error"))
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        await user.send_command("start")
        await _select_language(user, "en")
        await user.send_message("Alice")
        await user.send_message("15.03.1990")
        await user.send_message("London")

        with patch('horoscope.tasks.generate_horoscope_task') as mock_task:
            responses = await user.send_message("Berlin")

            assert len(responses) == 1
            assert "went wrong" in responses[0].text.lower() or "/start" in responses[0].text
            mock_task.delay.assert_not_called()

    async def test_subscription_activation_failure(self):
        from horoscope.handlers.subscription import successful_payment_handler

        mock_message = AsyncMock()
        mock_payment = MagicMock()
        mock_payment.telegram_payment_charge_id = "charge_123"
        mock_message.successful_payment = mock_payment

        user = UserEntity(telegram_uid=12345, language_code="en")

        profile_repo = _mock_profile_repo(profile=_make_profile())
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        mock_service = MagicMock()
        mock_service.aactivate_subscription = AsyncMock(
            side_effect=Exception("DB error")
        )

        with patch(
            'horoscope.handlers.subscription.container'
        ) as mock_container:
            mock_container.horoscope.subscription_service.return_value = mock_service
            await successful_payment_handler(message=mock_message, user=user)

        mock_message.answer.assert_called_once()
        call_text = mock_message.answer.call_args[0][0]
        assert "went wrong" in call_text.lower() or "support" in call_text.lower()
