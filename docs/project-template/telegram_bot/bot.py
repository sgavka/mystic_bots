"""
Bot instance configuration for aiogram.

This module provides helper functions to create and configure bot components.
Instantiation of bot, dispatcher, and storage should be done in the host code
(e.g., start_bot.py), not here.
"""
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import settings
from telegram_bot.middlewares.bot import BotMiddleware
from telegram_bot.middlewares.user import AppContextMiddleware, LoggingMiddleware, UserMiddleware
from telegram_bot.middlewares.i18n import create_i18n_middleware


def create_bot(bot_token: str) -> Bot:
    """
    Create a bot instance for the specified bot token.

    Args:
        bot_token: The token of the bot to create

    Returns:
        Bot instance configured with the bot's token
    """
    return Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


def create_storage() -> Union[RedisStorage, MemoryStorage]:
    """
    Create FSM storage based on environment configuration.

    Returns:
        RedisStorage if Redis is configured, otherwise MemoryStorage
    """
    if settings.REDIS_HOST and settings.REDIS_PORT:
        redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        return RedisStorage(redis=redis)
    else:
        return MemoryStorage()


def create_dispatcher(storage: BaseStorage) -> Dispatcher:
    """
    Create a dispatcher with the given storage.

    Args:
        storage: FSM storage instance

    Returns:
        Dispatcher instance
    """
    return Dispatcher(storage=storage)


def setup_middlewares(dispatcher: Dispatcher, bot_id: int) -> None:
    """
    Setup middlewares for the dispatcher.

    Args:
        dispatcher: The dispatcher to add middlewares to
        bot_id: Telegram bot ID for logging
    """
    # Bot middleware - injects bot_slug for multi-bot support
    bot_middleware = BotMiddleware(settings.CURRENT_BOT_SLUG)
    dispatcher.message.middleware(bot_middleware)
    dispatcher.callback_query.middleware(bot_middleware)
    dispatcher.inline_query.middleware(bot_middleware)

    # User middleware - handles user creation and loading
    user_middleware = UserMiddleware()
    dispatcher.message.middleware(user_middleware)
    dispatcher.callback_query.middleware(user_middleware)
    dispatcher.inline_query.middleware(user_middleware)

    # AppContext middleware - provides message management utilities
    app_context_middleware = AppContextMiddleware()
    dispatcher.message.middleware(app_context_middleware)
    dispatcher.callback_query.middleware(app_context_middleware)

    # Logging middleware - logs all messages to database
    logging_middleware = LoggingMiddleware(bot_id=bot_id)
    dispatcher.message.middleware(logging_middleware)
    dispatcher.callback_query.middleware(logging_middleware)

    # I18n middleware - handles translations based on user language
    i18n_middleware = create_i18n_middleware()
    dispatcher.message.middleware(i18n_middleware)
    dispatcher.callback_query.middleware(i18n_middleware)


def setup_handlers(dispatcher: Dispatcher) -> None:
    """
    Register all handlers.

    Args:
        dispatcher: The dispatcher to add handlers to
    """
    # TODO: Register error handler and bot-specific routers here
    pass


def setup_dispatcher(dispatcher: Dispatcher, bot_instance: Bot) -> Dispatcher:
    """
    Complete dispatcher setup with middlewares and handlers.

    Args:
        dispatcher: The dispatcher to configure
        bot_instance: Bot instance

    Returns:
        Configured dispatcher
    """
    setup_middlewares(dispatcher=dispatcher, bot_id=bot_instance.id)
    setup_handlers(dispatcher=dispatcher)

    return dispatcher
