from django.db import models

from horoscope.enums import HoroscopeType, Language, SubscriptionStatus


class UserProfile(models.Model):
    user_telegram_uid = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=255)
    place_of_living = models.CharField(max_length=255)
    preferred_language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.EN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        pass

    def __str__(self):
        return f"UserProfile {self.user_telegram_uid} ({self.name})"


class Horoscope(models.Model):
    id = models.AutoField(primary_key=True)
    user_telegram_uid = models.BigIntegerField()
    horoscope_type = models.CharField(
        max_length=50,
        choices=HoroscopeType.choices,
        default=HoroscopeType.DAILY,
    )
    date = models.DateField()
    full_text = models.TextField()
    teaser_text = models.TextField()
    extended_teaser_text = models.TextField(default='')
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_to_send_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_telegram_uid', 'date']),
            models.Index(fields=['user_telegram_uid', 'horoscope_type', 'date']),
        ]

    def __str__(self):
        return f"Horoscope {self.id} for user {self.user_telegram_uid} ({self.date})"


class LLMUsage(models.Model):
    id = models.AutoField(primary_key=True)
    horoscope = models.OneToOneField(
        Horoscope,
        on_delete=models.CASCADE,
        related_name='llm_usage',
    )
    model = models.CharField(max_length=256)
    input_tokens = models.PositiveIntegerField()
    output_tokens = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __str__(self):
        return f"LLMUsage {self.id} for horoscope {self.horoscope_id} ({self.model})"


class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    user_telegram_uid = models.BigIntegerField(unique=True)
    status = models.CharField(
        max_length=50,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    telegram_payment_charge_id = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_telegram_uid', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]

    def __str__(self):
        return f"Subscription {self.id} for user {self.user_telegram_uid} ({self.status})"


class HoroscopeFollowup(models.Model):
    id = models.AutoField(primary_key=True)
    horoscope = models.ForeignKey(
        Horoscope,
        on_delete=models.CASCADE,
        related_name='followups',
    )
    question_text = models.TextField()
    answer_text = models.TextField()
    model = models.CharField(max_length=256)
    input_tokens = models.PositiveIntegerField()
    output_tokens = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['horoscope']),
        ]

    def __str__(self):
        return f"HoroscopeFollowup {self.id} for horoscope {self.horoscope_id}"
