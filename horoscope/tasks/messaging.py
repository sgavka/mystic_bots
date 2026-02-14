"""
Shared messaging utilities for Celery tasks.
Handles sending Telegram messages from synchronous Celery task context.
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_message(telegram_uid: int, text: str, reply_markup=None) -> bool:
    """Send a single Telegram message via AppContext. Returns True on success."""
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from config import settings
    from telegram_bot.app_context import AppContext

    async def _send():
        bot = Bot(
            token=settings.CURRENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            app_context = AppContext.for_user(
                bot=bot,
                user_telegram_uid=telegram_uid,
            )
            await app_context.send_message(
                text=text,
                reply_markup=reply_markup,
            )
            return True
        except Exception as e:
            # Telegram API can raise various errors — must not crash the task
            logger.error(f"Failed to send message to user {telegram_uid}", exc_info=e)
            return False
        finally:
            await bot.session.close()

    return asyncio.run(_send())


def send_messages_batch(
    messages: list[tuple[int, str, Optional[object]]],
) -> int:
    """
    Send multiple Telegram messages reusing a single Bot session.

    Args:
        messages: List of (telegram_uid, text, reply_markup) tuples.

    Returns:
        Number of successfully sent messages.
    """
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from config import settings
    from telegram_bot.app_context import AppContext

    async def _send_all():
        bot = Bot(
            token=settings.CURRENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        sent = 0
        try:
            for telegram_uid, text, keyboard in messages:
                try:
                    app_context = AppContext.for_user(
                        bot=bot,
                        user_telegram_uid=telegram_uid,
                    )
                    await app_context.send_message(
                        text=text,
                        reply_markup=keyboard,
                    )
                    sent += 1
                except Exception as e:
                    # Telegram API can raise various errors — must not crash the batch loop
                    logger.error(f"Failed to send message to user {telegram_uid}", exc_info=e)
        finally:
            await bot.session.close()
        return sent

    return asyncio.run(_send_all())
