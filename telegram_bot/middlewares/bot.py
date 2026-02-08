from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.enums import BotSlug


class BotMiddleware(BaseMiddleware):
    def __init__(self, bot_slug: BotSlug):
        super().__init__()
        self.bot_slug = bot_slug

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data['bot_slug'] = self.bot_slug
        return await handler(event, data)
