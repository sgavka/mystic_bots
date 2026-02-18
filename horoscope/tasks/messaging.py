"""
Shared messaging utilities for background tasks.
All functions are async and use the shared bot instance from the event loop.
"""

import logging
from typing import Optional

from aiogram import Bot

logger = logging.getLogger(__name__)


async def send_message(
    bot: Bot,
    telegram_uid: int,
    text: str,
    reply_markup: Optional[object] = None,
) -> bool:
    """Send a single Telegram message via AppContext. Returns True on success."""
    from telegram_bot.app_context import AppContext

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


async def send_messages_batch(
    bot: Bot,
    messages: list[tuple[int, str, Optional[object]]],
) -> int:
    """
    Send multiple Telegram messages using the shared bot instance.

    Args:
        bot: The Bot instance to use for sending.
        messages: List of (telegram_uid, text, reply_markup) tuples.

    Returns:
        Number of successfully sent messages.
    """
    from telegram_bot.app_context import AppContext

    sent = 0
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
    return sent
