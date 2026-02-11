from django.core.management.base import BaseCommand

TASKS = {
    'generate-daily-horoscopes': 'horoscope.tasks.send_daily_horoscope.generate_daily_for_all_users_task',
    'send-daily-horoscope-notifications': 'horoscope.tasks.send_daily_horoscope.send_daily_horoscope_notifications_task',
    'send-expiry-reminders': 'horoscope.tasks.subscription_reminders.send_expiry_reminders_task',
    'send-expired-notifications': 'horoscope.tasks.subscription_reminders.send_expired_notifications_task',
}


class Command(BaseCommand):
    help = 'Run a Celery task synchronously from the terminal'

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
        task_func()

        self.stdout.write(self.style.SUCCESS(f'Task "{task_name}" completed.'))
