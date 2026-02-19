"""
Tests for horoscope/handlers/settings.py — /timezone and /notification_time commands.
Also tests for utility functions in the settings handler.
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from horoscope.entities import UserProfileEntity
from horoscope.handlers.settings import (
    _format_utc_offset,
    _local_hour_to_utc,
    _parse_timezone_offset,
    _utc_hour_to_local,
)


def _make_profile(
    telegram_uid: int = 12345,
    preferred_language: str = "en",
    timezone: str = "",
    notification_hour_utc: int | None = None,
) -> UserProfileEntity:
    return UserProfileEntity(
        user_telegram_uid=telegram_uid,
        name="Test",
        date_of_birth=date(1990, 5, 15),
        place_of_birth="London",
        place_of_living="Berlin",
        preferred_language=preferred_language,
        timezone=timezone,
        notification_hour_utc=notification_hour_utc,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


class TestFormatUtcOffset:
    def test_positive(self):
        assert _format_utc_offset(3) == "UTC+3"

    def test_negative(self):
        assert _format_utc_offset(-5) == "UTC-5"

    def test_zero(self):
        assert _format_utc_offset(0) == "UTC+0"

    def test_large_positive(self):
        assert _format_utc_offset(14) == "UTC+14"


class TestParseTimezoneOffset:
    def test_positive(self):
        assert _parse_timezone_offset("UTC+3") == 3

    def test_negative(self):
        assert _parse_timezone_offset("UTC-5") == -5

    def test_zero(self):
        assert _parse_timezone_offset("UTC+0") == 0

    def test_empty(self):
        assert _parse_timezone_offset("") == 0

    def test_invalid(self):
        assert _parse_timezone_offset("invalid") == 0

    def test_no_sign(self):
        assert _parse_timezone_offset("UTC") == 0


class TestLocalHourToUtc:
    def test_positive_offset(self):
        # 8:00 local in UTC+3 = 5:00 UTC
        assert _local_hour_to_utc(local_hour=8, utc_offset=3) == 5

    def test_negative_offset(self):
        # 8:00 local in UTC-5 = 13:00 UTC
        assert _local_hour_to_utc(local_hour=8, utc_offset=-5) == 13

    def test_wrap_around(self):
        # 2:00 local in UTC+5 = 21:00 UTC (previous day)
        assert _local_hour_to_utc(local_hour=2, utc_offset=5) == 21

    def test_zero_offset(self):
        assert _local_hour_to_utc(local_hour=8, utc_offset=0) == 8


class TestUtcHourToLocal:
    def test_positive_offset(self):
        # 5:00 UTC in UTC+3 = 8:00 local
        assert _utc_hour_to_local(utc_hour=5, utc_offset=3) == 8

    def test_negative_offset(self):
        # 13:00 UTC in UTC-5 = 8:00 local
        assert _utc_hour_to_local(utc_hour=13, utc_offset=-5) == 8

    def test_wrap_around(self):
        # 21:00 UTC in UTC+5 = 2:00 local (next day)
        assert _utc_hour_to_local(utc_hour=21, utc_offset=5) == 2

    def test_zero_offset(self):
        assert _utc_hour_to_local(utc_hour=8, utc_offset=0) == 8


class TestTimezoneCommand:
    @pytest.mark.django_db
    async def test_no_profile_shows_error(self):
        from horoscope.handlers.settings import timezone_command_handler

        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=None)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345
        mock_user.language_code = "en"

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        mock_message = MagicMock()
        mock_state = MagicMock()

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await timezone_command_handler(
                message=mock_message,
                state=mock_state,
                user=mock_user,
                app_context=mock_app_context,
            )

        mock_app_context.send_message.assert_called_once()
        text = mock_app_context.send_message.call_args[1]['text']
        assert "profile" in text.lower()

    @pytest.mark.django_db
    async def test_shows_timezone_keyboard_with_current(self):
        from horoscope.handlers.settings import timezone_command_handler

        profile = _make_profile(timezone="UTC+3")
        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        mock_message = MagicMock()
        mock_state = MagicMock()
        mock_state.clear = AsyncMock()

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await timezone_command_handler(
                message=mock_message,
                state=mock_state,
                user=mock_user,
                app_context=mock_app_context,
            )

        mock_app_context.send_message.assert_called_once()
        call_kwargs = mock_app_context.send_message.call_args[1]
        assert "UTC+3" in call_kwargs['text']
        assert call_kwargs['reply_markup'] is not None


class TestChangeTimezone:
    @pytest.mark.django_db
    async def test_updates_timezone(self):
        from horoscope.handlers.settings import change_timezone_callback

        updated_profile = _make_profile(timezone="UTC+5")
        mock_profile_repo = MagicMock()
        mock_profile_repo.aupdate_timezone = AsyncMock(return_value=updated_profile)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345

        mock_app_context = MagicMock()
        mock_app_context.edit_message = AsyncMock()
        mock_app_context.send_message = AsyncMock()

        mock_callback = MagicMock()
        mock_callback.answer = AsyncMock()
        mock_callback.message.message_id = 1

        mock_callback_data = MagicMock()
        mock_callback_data.offset = 5

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await change_timezone_callback(
                callback=mock_callback,
                callback_data=mock_callback_data,
                user=mock_user,
                app_context=mock_app_context,
            )

        mock_profile_repo.aupdate_timezone.assert_called_once_with(
            telegram_uid=12345,
            timezone="UTC+5",
        )
        mock_app_context.send_message.assert_called_once()
        assert "UTC+5" in mock_app_context.send_message.call_args[1]['text']


class TestNotificationTimeCommand:
    @pytest.mark.django_db
    async def test_requires_timezone_first(self):
        from horoscope.handlers.settings import notification_time_command_handler

        profile = _make_profile(timezone="")
        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        mock_message = MagicMock()
        mock_state = MagicMock()

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await notification_time_command_handler(
                message=mock_message,
                state=mock_state,
                user=mock_user,
                app_context=mock_app_context,
            )

        mock_app_context.send_message.assert_called_once()
        text = mock_app_context.send_message.call_args[1]['text']
        assert "timezone" in text.lower()

    @pytest.mark.django_db
    async def test_shows_notification_hour_keyboard(self):
        from horoscope.handlers.settings import notification_time_command_handler

        profile = _make_profile(timezone="UTC+3", notification_hour_utc=5)
        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345

        mock_app_context = MagicMock()
        mock_app_context.send_message = AsyncMock()

        mock_message = MagicMock()
        mock_state = MagicMock()
        mock_state.clear = AsyncMock()

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await notification_time_command_handler(
                message=mock_message,
                state=mock_state,
                user=mock_user,
                app_context=mock_app_context,
            )

        mock_app_context.send_message.assert_called_once()
        call_kwargs = mock_app_context.send_message.call_args[1]
        assert "08:00" in call_kwargs['text']  # UTC+3 offset: 5 UTC = 8 local
        assert call_kwargs['reply_markup'] is not None


class TestChangeNotificationHour:
    @pytest.mark.django_db
    async def test_converts_local_to_utc_and_saves(self):
        from horoscope.handlers.settings import change_notification_hour_callback

        profile = _make_profile(timezone="UTC+3")
        updated_profile = _make_profile(timezone="UTC+3", notification_hour_utc=5)
        mock_profile_repo = MagicMock()
        mock_profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
        mock_profile_repo.aupdate_notification_hour = AsyncMock(return_value=updated_profile)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345

        mock_app_context = MagicMock()
        mock_app_context.edit_message = AsyncMock()
        mock_app_context.send_message = AsyncMock()

        mock_callback = MagicMock()
        mock_callback.answer = AsyncMock()
        mock_callback.message.message_id = 1

        mock_callback_data = MagicMock()
        mock_callback_data.hour = 8  # 8:00 local

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await change_notification_hour_callback(
                callback=mock_callback,
                callback_data=mock_callback_data,
                user=mock_user,
                app_context=mock_app_context,
            )

        # 8:00 local in UTC+3 = 5:00 UTC
        mock_profile_repo.aupdate_notification_hour.assert_called_once_with(
            telegram_uid=12345,
            notification_hour_utc=5,
        )
        mock_app_context.send_message.assert_called_once()
        assert "08:00" in mock_app_context.send_message.call_args[1]['text']


class TestResetNotificationHour:
    @pytest.mark.django_db
    async def test_resets_to_none(self):
        from horoscope.handlers.settings import reset_notification_hour_callback

        updated_profile = _make_profile(timezone="UTC+3")
        mock_profile_repo = MagicMock()
        mock_profile_repo.aupdate_notification_hour = AsyncMock(return_value=updated_profile)

        mock_user = MagicMock()
        mock_user.telegram_uid = 12345

        mock_app_context = MagicMock()
        mock_app_context.edit_message = AsyncMock()
        mock_app_context.send_message = AsyncMock()

        mock_callback = MagicMock()
        mock_callback.answer = AsyncMock()
        mock_callback.message.message_id = 1

        with patch('horoscope.handlers.settings.container') as mock_container:
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo

            await reset_notification_hour_callback(
                callback=mock_callback,
                user=mock_user,
                app_context=mock_app_context,
            )

        mock_profile_repo.aupdate_notification_hour.assert_called_once_with(
            telegram_uid=12345,
            notification_hour_utc=None,
        )
        mock_app_context.send_message.assert_called_once()
        text = mock_app_context.send_message.call_args[1]['text']
        assert "reset" in text.lower() or "default" in text.lower()
