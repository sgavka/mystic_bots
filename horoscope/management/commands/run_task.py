import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.core.management.base import BaseCommand

from config import settings

TASKS = {
    'generate-daily-horoscopes': 'horoscope.tasks.send_daily_horoscope.generate_daily_for_all_users',
    'send-daily-horoscope-notifications': 'horoscope.tasks.send_daily_horoscope.send_daily_horoscope_notifications',
    'send-expiry-reminders': 'horoscope.tasks.subscription_reminders.send_expiry_reminders',
    'send-expired-notifications': 'horoscope.tasks.subscription_reminders.send_expired_notifications',
    'send-periodic-teaser-notifications': 'horoscope.tasks.send_periodic_teaser.send_periodic_teaser_notifications',
}


class Command(BaseCommand):
    help = 'Run a background task from the terminal'

    def add_arguments(self, parser):
        parser.add_argument(
            'task_name',
            type=str,
            choices=TASKS.keys(),
            help=f'Task to run. Available: {", ".join(TASKS.keys())}',
        )

    def handle(self, *args, **options):
        task_name = options['task_name']
        module_path, func_name = TASKS[task_name].rsplit('.', 1)

        self.stdout.write(f'Running task: {task_name}...')

        from importlib import import_module
        module = import_module(module_path)
        task_func = getattr(module, func_name)

        asyncio.run(self._run_task(task_func=task_func))

        self.stdout.write(self.style.SUCCESS(f'Task "{task_name}" completed.'))

    async def _run_task(self, task_func):
        bot = Bot(
            token=settings.CURRENT_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            await task_func(bot)
        finally:
            await bot.session.close()
