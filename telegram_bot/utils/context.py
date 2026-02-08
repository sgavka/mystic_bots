from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message


class AppContext:
    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

    async def send_message(
        self,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message:
        return await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_markup=reply_markup,
        )

    async def edit_message(
        self,
        message_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        return await self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
        )

    async def delete_message(self, message_id: int) -> bool:
        try:
            return await self.bot.delete_message(
                chat_id=self.chat_id,
                message_id=message_id,
            )
        except Exception:
            return False
