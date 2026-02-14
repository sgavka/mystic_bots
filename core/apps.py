from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self) -> None:
        """Initialize dependency injection wiring when Django app is ready."""
        from core.containers import container

        # Wire the container to all packages where @inject will be used
        # Using packages instead of individual modules allows automatic wiring
        # of all modules within the package, including dynamically loaded ones
        container.wire(
            packages=[
                'core',
                'telegram_bot',
                'horoscope',
            ]
        )
