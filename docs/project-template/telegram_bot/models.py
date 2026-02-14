from django.db import models


class MessageHistory(models.Model):
    """Model for logging all messages sent/received by the bot"""
    id = models.AutoField(primary_key=True)
    from_user_telegram_uid = models.BigIntegerField(null=True, blank=True)
    to_user_telegram_uid = models.BigIntegerField(null=True, blank=True)
    chat_telegram_uid = models.BigIntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    callback_query = models.CharField(max_length=255, null=True, blank=True)
    raw = models.JSONField(null=True, blank=True)
    context = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'message_history'
        indexes = [
            models.Index(fields=['from_user_telegram_uid']),
            models.Index(fields=['chat_telegram_uid']),
        ]

    def __str__(self):
        return f"Message {self.id} from {self.from_user_telegram_uid}"
