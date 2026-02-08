from django.db import models


class SettingType(models.TextChoices):
    STRING = 'string', 'String'
    INTEGER = 'integer', 'Integer'
    BOOLEAN = 'boolean', 'Boolean'
    JSON = 'json', 'JSON'


class BotSlug(models.TextChoices):
    HOROSCOPE = 'horoscope', 'Horoscope'

    @property
    def title(self) -> str:
        return self.label
