"""
BotMiddleware - Injects bot_slug into handler context
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.enums import BotSlug


class BotMiddleware(BaseMiddleware):
    """
    Middleware to inject bot_slug into all handlers.
    """

    def __init__(self, bot_slug: BotSlug):
        """
        Initialize BotMiddleware.

        Args:
            bot_slug: Bot identifier.
        """
        super().__init__()
        self.bot_slug = bot_slug

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Inject bot_slug into handler context.
        """
        data['bot_slug'] = self.bot_slug
        return await handler(event, data)
