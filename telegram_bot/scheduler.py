"""
Asyncio-based scheduler for periodic background tasks.
Replaces Celery Beat for running daily tasks within the bot's event loop.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine

from aiogram import Bot

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """Simple asyncio-based scheduler for periodic tasks."""

    def __init__(self, bot: Bot):
        self._bot = bot
        self._tasks: list[asyncio.Task] = []

    @property
    def bot(self) -> Bot:
        return self._bot

    def schedule(
        self,
        func: Callable[[Bot], Coroutine[Any, Any, Any]],
        interval_seconds: int,
        name: str,
    ) -> None:
        """Schedule an async function to run periodically."""
        task = asyncio.create_task(
            self._run_periodic(
                func=func,
                interval_seconds=interval_seconds,
                name=name,
            ),
            name=f"scheduler:{name}",
        )
        self._tasks.append(task)

    async def _run_periodic(
        self,
        func: Callable[[Bot], Coroutine[Any, Any, Any]],
        interval_seconds: int,
        name: str,
    ) -> None:
        """Run a function periodically with error handling."""
        while True:
            try:
                logger.info(f"Running scheduled task: {name}")
                await func(self._bot)
                logger.info(f"Scheduled task completed: {name}")
            except asyncio.CancelledError:
                logger.info(f"Scheduled task cancelled: {name}")
                break
            except Exception as e:
                # Periodic task failure must not crash the scheduler loop
                logger.error(f"Scheduled task failed: {name}", exc_info=e)
            await asyncio.sleep(interval_seconds)

    async def shutdown(self) -> None:
        """Cancel all scheduled tasks and wait for them to finish."""
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("Background scheduler stopped")
