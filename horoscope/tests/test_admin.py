"""Tests for admin command handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from horoscope.handlers.admin import refund_command_handler, stats_command_handler


def _make_user_entity(telegram_uid: int = 12345):
    user = MagicMock()
    user.telegram_uid = telegram_uid
    return user


class TestRefundCommand:

    @pytest.mark.asyncio
    async def test_non_admin_is_ignored(self):
        message = AsyncMock()
        message.text = "/refund charge_123"
        user = _make_user_entity(telegram_uid=99999)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_charge_id_shows_usage(self):
        message = AsyncMock()
        message.text = "/refund"
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_called_once()
        assert "Usage" in app_context.send_message.call_args[1]['text']

    @pytest.mark.asyncio
    async def test_successful_refund(self):
        message = AsyncMock()
        message.text = "/refund charge_123"
        message.from_user.id = 12345
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.bot.refund_star_payment.assert_called_once_with(
            user_id=12345,
            telegram_payment_charge_id="charge_123",
        )
        app_context.send_message.assert_called_once()
        assert "successful" in app_context.send_message.call_args[1]['text']

    @pytest.mark.asyncio
    async def test_refund_api_failure(self):
        message = AsyncMock()
        message.text = "/refund charge_123"
        message.from_user.id = 12345
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()
        app_context.bot.refund_star_payment = AsyncMock(
            side_effect=Exception("Telegram API error"),
        )

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await refund_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_called_once()
        assert "failed" in app_context.send_message.call_args[1]['text'].lower()


class TestStatsCommand:

    @pytest.mark.asyncio
    async def test_non_admin_is_ignored(self):
        message = AsyncMock()
        user = _make_user_entity(telegram_uid=99999)
        app_context = AsyncMock()

        with patch('horoscope.handlers.admin.settings') as mock_settings:
            mock_settings.ADMIN_USERS_IDS = [12345]

            await stats_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_stats_returns_data(self):
        message = AsyncMock()
        user = _make_user_entity(telegram_uid=12345)
        app_context = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.count.return_value = 100
        mock_profile_repo.count_created_since.return_value = 5

        mock_subscription_repo = MagicMock()
        mock_subscription_repo.count.return_value = 50
        mock_subscription_repo.count_active.return_value = 30
        mock_subscription_repo.count_created_since.return_value = 2

        mock_horoscope_repo = MagicMock()
        mock_horoscope_repo.count.return_value = 500
        mock_horoscope_repo.count_created_since.return_value = 10

        mock_followup_repo = MagicMock()
        mock_followup_repo.count.return_value = 25

        with patch('horoscope.handlers.admin.settings') as mock_settings, \
             patch('horoscope.handlers.admin.container') as mock_container:
            mock_settings.ADMIN_USERS_IDS = [12345]
            mock_container.horoscope.user_profile_repository.return_value = mock_profile_repo
            mock_container.horoscope.subscription_repository.return_value = mock_subscription_repo
            mock_container.horoscope.horoscope_repository.return_value = mock_horoscope_repo
            mock_container.horoscope.followup_repository.return_value = mock_followup_repo

            await stats_command_handler(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_called_once()
        text = app_context.send_message.call_args[1]['text']
        assert "100" in text
        assert "50" in text
        assert "30" in text
        assert "500" in text
        assert "25" in text
        assert "5" in text
        assert "2" in text
        assert "10" in text
        assert "Stats" in text
        assert "Total" in text
        assert "Today" in text
