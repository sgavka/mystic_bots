import asyncio
import logging
import sys

from django.core.management.base import BaseCommand

from config import settings
from core.enums import BotSlug
from telegram_bot.bot import create_bot, create_storage, create_dispatcher, setup_dispatcher


class Command(BaseCommand):
    help = 'Run the Telegram bot with aiogram'

    def add_arguments(self, parser):
        parser.add_argument(
            '--log-level',
            type=str,
            default='INFO',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Set the logging level (default: INFO)',
        )
        parser.add_argument(
            '--bot',
            type=str,
            default=None,
            help=f'Bot slug to run (default: {settings.MAIN_BOT_SLUG}). '
                 f'Available: {", ".join(slug.value for slug in BotSlug)}',
        )

    def handle(self, *args, **options):
        bot_slug = options.get('bot')
        if bot_slug is None:
            bot_slug = settings.MAIN_BOT_SLUG

        valid_slugs = [slug.value for slug in BotSlug]
        if bot_slug not in valid_slugs:
            self.stderr.write(
                self.style.ERROR(
                    f'Invalid bot slug: "{bot_slug}". '
                    f'Available: {", ".join(valid_slugs)}'
                )
            )
            sys.exit(1)

        bot_config = settings.BOTS_CONFIG[bot_slug]
        settings.CURRENT_BOT_SLUG = BotSlug(bot_config['slug'])
        settings.CURRENT_BOT_TOKEN = bot_config['token']

        logging.info(f'Starting bot "{bot_slug}"')

        try:
            asyncio.run(self.run_bot())
        except KeyboardInterrupt:
            logging.info("Bot stopped by user (Ctrl+C)")

    async def run_bot(self):
        logger = logging.getLogger(__name__)

        bot = create_bot(settings.CURRENT_BOT_TOKEN)
        storage = create_storage()
        dispatcher = create_dispatcher(storage=storage)

        self._bot = bot
        self._scheduler = None

        try:
            setup_dispatcher(dispatcher=dispatcher, bot_instance=bot)

            dispatcher.startup.register(self.on_startup)
            dispatcher.shutdown.register(self.on_shutdown)

            logger.info(f"Bot '{settings.CURRENT_BOT_SLUG}' polling started.")
            await dispatcher.start_polling(
                bot,
                allowed_updates=dispatcher.resolve_used_update_types(),
            )
        finally:
            await bot.session.close()
            logger.info("Bot session closed")

    async def on_startup(self):
        logger = logging.getLogger(__name__)

        from telegram_bot.scheduler import BackgroundScheduler
        from horoscope.tasks import (
            generate_daily_for_all_users,
            send_daily_horoscope_notifications,
            send_periodic_teaser_notifications,
            send_expiry_reminders,
            send_expired_notifications,
        )

        self._scheduler = BackgroundScheduler(bot=self._bot)

        daily_interval = settings.SCHEDULER_DAILY_INTERVAL_SECONDS
        hourly_interval = settings.SCHEDULER_HOURLY_INTERVAL_SECONDS

        # Horoscope generation and notification tasks run hourly
        # to support per-user notification hours
        self._scheduler.schedule(
            func=generate_daily_for_all_users,
            interval_seconds=hourly_interval,
            name="generate-daily-horoscopes",
        )
        self._scheduler.schedule(
            func=send_daily_horoscope_notifications,
            interval_seconds=1 * 60,
            name="send-daily-horoscope-notifications",
        )
        self._scheduler.schedule(
            func=send_periodic_teaser_notifications,
            interval_seconds=30 * 60,
            name="send-periodic-teaser-notifications",
        )
        # Subscription tasks remain on daily interval
        self._scheduler.schedule(
            func=send_expiry_reminders,
            interval_seconds=daily_interval,
            name="send-expiry-reminders",
        )
        self._scheduler.schedule(
            func=send_expired_notifications,
            interval_seconds=daily_interval,
            name="send-expired-notifications",
        )

        logger.info("=" * 60)
        logger.info("Bot startup complete")
        logger.info(
            f"Background scheduler started: "
            f"horoscope tasks={hourly_interval}s, subscription tasks={daily_interval}s"
        )
        logger.info("=" * 60)

    async def on_shutdown(self):
        logger = logging.getLogger(__name__)
        if self._scheduler:
            await self._scheduler.shutdown()
        logger.info("=" * 60)
        logger.info("Bot shutting down...")
        logger.info("=" * 60)
