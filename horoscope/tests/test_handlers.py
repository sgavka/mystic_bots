"""
Tests for horoscope bot handlers using aiogram-test-framework.
Covers all user flows: wizard onboarding, horoscope view, subscription.
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

    dispatcher.include_router(wizard_router)
    dispatcher.include_router(horoscope_router)
    dispatcher.include_router(subscription_router)


def _make_profile(
    telegram_uid: int = 100000,
    name: str = "Test User",
    date_of_birth: date = date(1990, 5, 15),
    place_of_birth: str = "London",
    place_of_living: str = "Berlin",
) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name=name,
        date_of_birth=date_of_birth,
        place_of_birth=place_of_birth,
        place_of_living=place_of_living,
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
# Wizard: /start
# ---------------------------------------------------------------------------

class TestWizardStart:

    async def test_start_new_user(self, client):
        profile_repo = _mock_profile_repo(profile=None)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="John")
        responses = await user.send_command("start")

        assert len(responses) == 1
        assert "Mystic Horoscope" in responses[0].text
        assert "name" in responses[0].text.lower()

    async def test_start_returning_user(self, client):
        profile = _make_profile(name="Alice")
        profile_repo = _mock_profile_repo(profile=profile)
        container.horoscope.user_profile_repository.override(
            providers.Object(profile_repo)
        )

        user = client.create_user(first_name="Alice")
        responses = await user.send_command("start")

        assert len(responses) == 1
        assert "Welcome back" in responses[0].text
        assert "Alice" in responses[0].text


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
        assert "valid name" in responses[0].text.lower()

    async def test_name_too_long(self, client):
        user = await self._enter_wizard(client)
        responses = await user.send_message("A" * 101)

        assert len(responses) == 1
        assert "valid name" in responses[0].text.lower()


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
        await user.send_message("Alice")
        await user.send_message("15.03.1990")
        return user

    async def test_valid_place(self, client):
        user = await self._enter_pob_step(client)
        responses = await user.send_message("London")

        assert len(responses) == 1
        assert "place of living" in responses[0].text.lower()

    async def test_place_too_short(self, client):
        user = await self._enter_pob_step(client)
        responses = await user.send_message("A")

        assert len(responses) == 1
        assert "valid city" in responses[0].text.lower()


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
        assert "valid city" in responses[0].text.lower()


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

        # Step 1: /start
        responses = await user.send_command("start")
        assert "Mystic Horoscope" in responses[0].text

        # Step 2: name
        responses = await user.send_message("Alice")
        assert "Alice" in responses[0].text
        assert "date of birth" in responses[0].text.lower()

        # Step 3: date of birth
        responses = await user.send_message("15.03.1990")
        assert "place of birth" in responses[0].text.lower()

        # Step 4: place of birth
        responses = await user.send_message("London")
        assert "place of living" in responses[0].text.lower()

        # Step 5: place of living → profile created, horoscope queued
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
        assert "subscribe" in responses[0].text.lower()


# ---------------------------------------------------------------------------
# Subscription handler
# ---------------------------------------------------------------------------

class TestSubscription:

    async def test_subscribe_callback(self, client):
        user = client.create_user(first_name="John")
        responses = await user.click_button("subscribe")

        # Handler calls callback.answer() and then sends messages
        callback_answers = client.capture.get_callback_answers()
        assert len(callback_answers) >= 1

        sent_messages = client.capture.get_sent_messages()
        has_subscribe_info = any(
            "subscribe" in (m.text or "").lower()
            for m in sent_messages
        )
        assert has_subscribe_info
