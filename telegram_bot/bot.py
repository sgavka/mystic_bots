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
from telegram_bot.middlewares.i18n import UserLanguageMiddleware
from telegram_bot.middlewares.user import AppContextMiddleware, LoggingMiddleware, UserMiddleware


def create_bot(bot_token: str) -> Bot:
    return Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_storage() -> Union[RedisStorage, MemoryStorage]:
    if settings.REDIS_HOST and settings.REDIS_PORT:
        redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        return RedisStorage(redis=redis)
    else:
        return MemoryStorage()


def create_dispatcher(storage: BaseStorage) -> Dispatcher:
    return Dispatcher(storage=storage)


def setup_middlewares(dispatcher: Dispatcher, bot_instance: Bot) -> None:
    bot_middleware = BotMiddleware(settings.CURRENT_BOT_SLUG)
    dispatcher.message.middleware(bot_middleware)
    dispatcher.callback_query.middleware(bot_middleware)

    user_middleware = UserMiddleware()
    dispatcher.message.middleware(user_middleware)
    dispatcher.callback_query.middleware(user_middleware)

    app_context_middleware = AppContextMiddleware()
    dispatcher.message.middleware(app_context_middleware)
    dispatcher.callback_query.middleware(app_context_middleware)

    logging_middleware = LoggingMiddleware(bot_id=bot_instance.id)
    dispatcher.message.middleware(logging_middleware)
    dispatcher.callback_query.middleware(logging_middleware)

    i18n_middleware = UserLanguageMiddleware()
    dispatcher.message.middleware(i18n_middleware)
    dispatcher.callback_query.middleware(i18n_middleware)


def setup_handlers(dispatcher: Dispatcher) -> None:
    from telegram_bot.handlers import errors
    from horoscope.handlers.wizard import router as wizard_router
    from horoscope.handlers.horoscope import router as horoscope_router
    from horoscope.handlers.subscription import router as subscription_router
    from horoscope.handlers.language import router as language_router
    from horoscope.handlers.followup import router as followup_router
    from horoscope.handlers.admin import router as admin_router

    dispatcher.errors.register(errors.error_handler)
    dispatcher.include_router(wizard_router)
    dispatcher.include_router(horoscope_router)
    dispatcher.include_router(subscription_router)
    dispatcher.include_router(language_router)
    dispatcher.include_router(admin_router)
    # followup_router MUST be last — it catches any text message as a followup question
    dispatcher.include_router(followup_router)


def setup_dispatcher(dispatcher: Dispatcher, bot_instance: Bot) -> Dispatcher:
    setup_middlewares(dispatcher=dispatcher, bot_instance=bot_instance)
    setup_handlers(dispatcher=dispatcher)
    return dispatcher
