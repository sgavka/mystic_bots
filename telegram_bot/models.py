from django.db import models


class MessageHistory(models.Model):
    id = models.AutoField(primary_key=True)
    from_user_telegram_uid = models.BigIntegerField()
    to_user_telegram_uid = models.BigIntegerField(null=True, blank=True)
    chat_telegram_uid = models.BigIntegerField()

    text = models.TextField(null=True, blank=True)
    callback_query = models.CharField(max_length=255, null=True, blank=True)

    raw = models.JSONField(null=True, blank=True)
    context = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['from_user_telegram_uid', 'created_at']),
            models.Index(fields=['chat_telegram_uid', 'created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['callback_query']),
        ]

    def __str__(self) -> str:
        return f"Message {self.id} from {self.from_user_telegram_uid}"
