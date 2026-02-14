"""Tests for MessageHistory model, entity, and repository."""

from datetime import timedelta

import pytest
from django.utils import timezone

from telegram_bot.entities import MessageHistoryEntity
from telegram_bot.exceptions import MessageHistoryNotFoundException
from telegram_bot.models import MessageHistory
from telegram_bot.repositories.message_history import MessageHistoryRepository


@pytest.mark.django_db
class TestMessageHistoryRepository:

    def setup_method(self):
        self.repo = MessageHistoryRepository()

    def test_log_message_basic(self):
        entity = self.repo.log_message(
            from_user_telegram_uid=12345,
            chat_telegram_uid=12345,
            text="Hello bot",
        )
        assert isinstance(entity, MessageHistoryEntity)
        assert entity.from_user_telegram_uid == 12345
        assert entity.chat_telegram_uid == 12345
        assert entity.text == "Hello bot"
        assert entity.callback_query is None
        assert entity.id is not None

    def test_log_message_with_callback(self):
        entity = self.repo.log_message(
            from_user_telegram_uid=12345,
            chat_telegram_uid=12345,
            callback_query="subscribe",
        )
        assert entity.callback_query == "subscribe"
        assert entity.text is None

    def test_log_message_with_all_fields(self):
        entity = self.repo.log_message(
            from_user_telegram_uid=12345,
            chat_telegram_uid=67890,
            text="Test message",
            callback_query=None,
            to_user_telegram_uid=99999,
            raw={"message_id": 1},
            context={"handler": "test"},
        )
        assert entity.to_user_telegram_uid == 99999
        assert entity.raw == {"message_id": 1}
        assert entity.context == {"handler": "test"}

    def test_get_by_user(self):
        self.repo.log_message(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="Message 1",
        )
        self.repo.log_message(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="Message 2",
        )
        self.repo.log_message(
            from_user_telegram_uid=222,
            chat_telegram_uid=222,
            text="Other user",
        )

        messages = self.repo.get_by_user(telegram_uid=111)
        assert len(messages) == 2
        assert all(m.from_user_telegram_uid == 111 for m in messages)

    def test_get_by_user_with_limit(self):
        for i in range(5):
            self.repo.log_message(
                from_user_telegram_uid=111,
                chat_telegram_uid=111,
                text=f"Message {i}",
            )

        messages = self.repo.get_by_user(telegram_uid=111, limit=3)
        assert len(messages) == 3

    def test_get_by_user_empty(self):
        messages = self.repo.get_by_user(telegram_uid=999)
        assert messages == []

    def test_count_by_user(self):
        for _ in range(3):
            self.repo.log_message(
                from_user_telegram_uid=111,
                chat_telegram_uid=111,
                text="test",
            )
        self.repo.log_message(
            from_user_telegram_uid=222,
            chat_telegram_uid=222,
            text="other",
        )

        assert self.repo.count_by_user(telegram_uid=111) == 3
        assert self.repo.count_by_user(telegram_uid=222) == 1
        assert self.repo.count_by_user(telegram_uid=999) == 0

    def test_count_by_user_with_since(self):
        self.repo.log_message(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="recent",
        )
        # Manually set old created_at
        old_msg = MessageHistory.objects.create(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="old",
        )
        MessageHistory.objects.filter(pk=old_msg.pk).update(
            created_at=timezone.now() - timedelta(days=10),
        )

        since = timezone.now() - timedelta(days=1)
        assert self.repo.count_by_user(telegram_uid=111, since=since) == 1

    def test_delete_old_messages(self):
        self.repo.log_message(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="recent",
        )
        old_msg = MessageHistory.objects.create(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="old",
        )
        MessageHistory.objects.filter(pk=old_msg.pk).update(
            created_at=timezone.now() - timedelta(days=60),
        )

        deleted = self.repo.delete_old_messages(days=30)
        assert deleted == 1
        assert MessageHistory.objects.count() == 1

    def test_get_returns_entity(self):
        entity = self.repo.log_message(
            from_user_telegram_uid=111,
            chat_telegram_uid=111,
            text="test",
        )
        fetched = self.repo.get(pk=entity.id)
        assert fetched.id == entity.id
        assert fetched.text == "test"

    def test_get_not_found(self):
        with pytest.raises(MessageHistoryNotFoundException):
            self.repo.get(pk=99999)


@pytest.mark.django_db
class TestMessageHistoryEntity:

    def setup_method(self):
        MessageHistory.objects.all().delete()

    def test_from_model(self):
        model = MessageHistory.objects.create(
            from_user_telegram_uid=12345,
            chat_telegram_uid=67890,
            text="Test",
        )
        entity = MessageHistoryEntity.from_model(model)
        assert entity.from_user_telegram_uid == 12345
        assert entity.chat_telegram_uid == 67890
        assert entity.text == "Test"

    def test_from_models(self):
        for i in range(3):
            MessageHistory.objects.create(
                from_user_telegram_uid=12345,
                chat_telegram_uid=12345,
                text=f"Msg {i}",
            )
        models = MessageHistory.objects.all()
        entities = MessageHistoryEntity.from_models(list(models))
        assert len(entities) == 3
        assert all(isinstance(e, MessageHistoryEntity) for e in entities)
