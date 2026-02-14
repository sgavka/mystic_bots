"""
Django management command to run the Telegram bot

Usage:
    python manage.py start_bot
    python manage.py start_bot --bot bot_name
"""
import asyncio
import logging
import sys

from django.core.management.base import BaseCommand

from config import settings
from core.enums import BotSlug
from telegram_bot.bot import create_bot, create_storage, create_dispatcher, setup_dispatcher


class Command(BaseCommand):
    """
    Django management command to run the Telegram bot
    """
    help = 'Run the Telegram bot with aiogram'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--log-level',
            type=str,
            default='INFO',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Set the logging level (default: INFO)'
        )
        parser.add_argument(
            '--bot',
            type=str,
            default=None,
            help=f'Bot slug to run (default: {settings.MAIN_BOT_SLUG}). '
                 f'Available bots: {", ".join(slug.value for slug in BotSlug)}'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        bot_slug = options.get('bot')
        if bot_slug is None:
            bot_slug = settings.MAIN_BOT_SLUG

        valid_slugs = [slug.value for slug in BotSlug]
        if bot_slug not in valid_slugs:
            self.stderr.write(
                self.style.ERROR(
                    f'Invalid bot slug: "{bot_slug}". '
                    f'Available bots: {", ".join(valid_slugs)}'
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
        """Main async function to run the bot"""
        logger = logging.getLogger(__name__)

        # Create bot, storage, and dispatcher here (host code)
        bot = create_bot(settings.CURRENT_BOT_TOKEN)
        storage = create_storage()
        dispatcher = create_dispatcher(storage=storage)

        try:
            # Setup middlewares and handlers using helpers
            setup_dispatcher(dispatcher=dispatcher, bot_instance=bot)

            dispatcher.startup.register(self.on_startup)
            dispatcher.shutdown.register(self.on_shutdown)

            logger.info(f"Bot '{settings.CURRENT_BOT_SLUG}' polling started. Press Ctrl+C to stop.")
            await dispatcher.start_polling(
                bot,
                allowed_updates=dispatcher.resolve_used_update_types()
            )

        finally:
            await bot.session.close()
            logger.info("Bot session closed")

    async def on_startup(self):
        """Actions to perform on bot startup"""
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Bot startup complete")
        # TODO: Start background tasks here if needed
        logger.info("=" * 60)

    async def on_shutdown(self):
        """Actions to perform on bot shutdown"""
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Bot shutting down...")
        logger.info("=" * 60)
