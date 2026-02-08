import logging

from aiogram.types import ErrorEvent


logger = logging.getLogger(__name__)


async def error_handler(event: ErrorEvent):
    logger.error(
        f"Error in handler: {event.exception}",
        exc_info=event.exception,
    )
