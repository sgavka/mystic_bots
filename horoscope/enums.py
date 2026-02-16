from django.db import models


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'


class HoroscopeType(models.TextChoices):
    DAILY = 'daily', 'Daily'
    FIRST = 'first', 'First (onboarding)'


class Language(models.TextChoices):
    EN = 'en', 'English'
    RU = 'ru', 'Russian'
    UK = 'uk', 'Ukrainian'
    DE = 'de', 'German'
    HI = 'hi', 'Hindi'
    AR = 'ar', 'Arabic'
