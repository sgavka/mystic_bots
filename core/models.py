import json

from django.db import models

from core.enums import SettingType


class Setting(models.Model):
    name = models.CharField(max_length=256, primary_key=True)
    value = models.JSONField()
    type = models.CharField(
        max_length=256,
        choices=SettingType.choices,
        default=SettingType.STRING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'settings'

    def __str__(self):
        return f"Setting {self.name} = {self.value}"

    def get_value(self):
        if self.type == SettingType.STRING:
            return str(self.value)
        elif self.type == SettingType.INTEGER:
            return int(self.value)
        elif self.type == SettingType.BOOLEAN:
            return bool(self.value)
        elif self.type == SettingType.JSON:
            return self.value
        return self.value

    def set_value(self, value):
        if self.type == SettingType.STRING:
            self.value = str(value)
        elif self.type == SettingType.INTEGER:
            self.value = int(value)
        elif self.type == SettingType.BOOLEAN:
            self.value = bool(value)
        elif self.type == SettingType.JSON:
            if isinstance(value, str):
                self.value = json.loads(value)
            else:
                self.value = value


class User(models.Model):
    telegram_uid = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=15, null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'users'
        indexes = [
            models.Index(fields=['language_code']),
            models.Index(fields=['is_premium']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f"User {self.telegram_uid} ({self.username})"
