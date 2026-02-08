from django.db import models


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'


class HoroscopeType(models.TextChoices):
    DAILY = 'daily', 'Daily'
    FIRST = 'first', 'First (onboarding)'
