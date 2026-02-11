"""
Tests for core module: models, entities, repositories.
Covers Setting model, User model, BaseRepository, UserRepository,
SettingEntity, UserEntity, BaseEntity.
"""

import pytest

from core.base_entity import BaseEntity
from core.entities import SettingEntity, UserEntity
from core.enums import SettingType
from core.exceptions import UserNotFoundException
from core.models import Setting, User
from core.repositories.user import UserRepository


@pytest.mark.django_db
class TestSettingModel:
    def test_str(self):
        setting = Setting.objects.create(
            name="test_setting",
            value="hello",
            type=SettingType.STRING,
        )
        assert str(setting) == "Setting test_setting = hello"

    def test_get_value_string(self):
        setting = Setting.objects.create(
            name="str_setting",
            value="test_value",
            type=SettingType.STRING,
        )
        assert setting.get_value() == "test_value"
        assert isinstance(setting.get_value(), str)

    def test_get_value_integer(self):
        setting = Setting.objects.create(
            name="int_setting",
            value=42,
            type=SettingType.INTEGER,
        )
        assert setting.get_value() == 42
        assert isinstance(setting.get_value(), int)

    def test_get_value_boolean(self):
        setting = Setting.objects.create(
            name="bool_setting",
            value=True,
            type=SettingType.BOOLEAN,
        )
        assert setting.get_value() is True

    def test_get_value_json(self):
        setting = Setting.objects.create(
            name="json_setting",
            value={"key": "value"},
            type=SettingType.JSON,
        )
        result = setting.get_value()
        assert result == {"key": "value"}

    def test_set_value_string(self):
        setting = Setting.objects.create(
            name="str_set",
            value="",
            type=SettingType.STRING,
        )
        setting.set_value(123)
        assert setting.value == "123"

    def test_set_value_integer(self):
        setting = Setting.objects.create(
            name="int_set",
            value=0,
            type=SettingType.INTEGER,
        )
        setting.set_value("42")
        assert setting.value == 42

    def test_set_value_boolean(self):
        setting = Setting.objects.create(
            name="bool_set",
            value=False,
            type=SettingType.BOOLEAN,
        )
        setting.set_value(1)
        assert setting.value is True

    def test_set_value_json_from_string(self):
        setting = Setting.objects.create(
            name="json_set",
            value={},
            type=SettingType.JSON,
        )
        setting.set_value('{"a": 1}')
        assert setting.value == {"a": 1}

    def test_set_value_json_from_dict(self):
        setting = Setting.objects.create(
            name="json_set2",
            value={},
            type=SettingType.JSON,
        )
        setting.set_value({"b": 2})
        assert setting.value == {"b": 2}


@pytest.mark.django_db
class TestUserModel:
    def test_str(self):
        user = User.objects.create(
            telegram_uid=12345,
            username="testuser",
        )
        assert str(user) == "User 12345 (testuser)"

    def test_str_no_username(self):
        user = User.objects.create(telegram_uid=12345)
        assert str(user) == "User 12345 (None)"


class TestSettingEntity:
    def test_get_typed_value_string(self):
        from datetime import datetime

        entity = SettingEntity(
            name="test",
            value=42,
            type="string",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        result = entity.get_typed_value()
        assert result == "42"
        assert isinstance(result, str)

    def test_get_typed_value_integer(self):
        from datetime import datetime

        entity = SettingEntity(
            name="test",
            value="42",
            type="integer",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        assert entity.get_typed_value() == 42

    def test_get_typed_value_boolean(self):
        from datetime import datetime

        entity = SettingEntity(
            name="test",
            value=1,
            type="boolean",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        assert entity.get_typed_value() is True

    def test_get_typed_value_json(self):
        from datetime import datetime

        entity = SettingEntity(
            name="test",
            value={"key": "val"},
            type="json",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        assert entity.get_typed_value() == {"key": "val"}

    def test_get_typed_value_unknown_type(self):
        from datetime import datetime

        entity = SettingEntity(
            name="test",
            value="raw",
            type="unknown",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        assert entity.get_typed_value() == "raw"


class TestUserEntity:
    def test_full_name_with_first_and_last(self):
        entity = UserEntity(
            telegram_uid=123,
            first_name="John",
            last_name="Doe",
        )
        assert entity.full_name == "John Doe"

    def test_full_name_first_only(self):
        entity = UserEntity(
            telegram_uid=123,
            first_name="John",
        )
        assert entity.full_name == "John"

    def test_full_name_last_only(self):
        entity = UserEntity(
            telegram_uid=123,
            last_name="Doe",
        )
        assert entity.full_name == "Doe"

    def test_full_name_fallback_to_username(self):
        entity = UserEntity(
            telegram_uid=123,
            username="johndoe",
        )
        assert entity.full_name == "johndoe"

    def test_full_name_fallback_to_telegram_uid(self):
        entity = UserEntity(telegram_uid=123)
        assert entity.full_name == "123"


class TestBaseEntity:
    def test_from_models(self):
        class SimpleEntity(BaseEntity):
            value: int

        class FakeModel:
            value = 1

        class FakeModel2:
            value = 2

        results = SimpleEntity.from_models([FakeModel(), FakeModel2()])
        assert len(results) == 2
        assert results[0].value == 1
        assert results[1].value == 2

    def test_to_model_raises(self):
        entity = UserEntity(telegram_uid=123)
        with pytest.raises(NotImplementedError, match="to_model"):
            entity.to_model()


@pytest.mark.django_db
class TestUserRepository:
    def setup_method(self):
        self.repo = UserRepository()

    def test_get_found(self):
        User.objects.create(
            telegram_uid=12345,
            username="alice",
            first_name="Alice",
        )

        result = self.repo.get(12345)
        assert isinstance(result, UserEntity)
        assert result.telegram_uid == 12345
        assert result.username == "alice"

    def test_get_not_found(self):
        with pytest.raises(UserNotFoundException):
            self.repo.get(99999)

    def test_get_or_create_new(self):
        entity, created = self.repo.get_or_create(
            telegram_uid=12345,
            defaults={"username": "alice", "first_name": "Alice"},
        )

        assert created is True
        assert isinstance(entity, UserEntity)
        assert entity.telegram_uid == 12345
        assert entity.username == "alice"

    def test_get_or_create_existing(self):
        User.objects.create(
            telegram_uid=12345,
            username="alice",
        )

        entity, created = self.repo.get_or_create(
            telegram_uid=12345,
            defaults={"username": "bob"},
        )

        assert created is False
        assert entity.username == "alice"

    def test_update_by_pk_found(self):
        User.objects.create(
            telegram_uid=12345,
            username="alice",
        )

        result = self.repo.update_by_pk(12345, username="alice_updated")

        assert result is not None
        assert result.username == "alice_updated"
        assert User.objects.get(telegram_uid=12345).username == "alice_updated"

    def test_update_by_pk_not_found(self):
        result = self.repo.update_by_pk(99999, username="nobody")
        assert result is None

    def test_update_or_create_new(self):
        entity, created = self.repo.update_or_create(
            telegram_uid=12345,
            defaults={"username": "alice"},
        )

        assert created is True
        assert entity.telegram_uid == 12345
        assert entity.username == "alice"

    def test_update_or_create_existing(self):
        User.objects.create(
            telegram_uid=12345,
            username="alice",
        )

        entity, created = self.repo.update_or_create(
            telegram_uid=12345,
            defaults={"username": "alice_updated"},
        )

        assert created is False
        assert entity.username == "alice_updated"


@pytest.mark.django_db
class TestBaseRepositoryViaUser:
    """Test BaseRepository methods through UserRepository."""

    def setup_method(self):
        self.repo = UserRepository()

    def test_delete_hard_delete(self):
        User.objects.create(telegram_uid=12345, username="alice")

        result = self.repo.delete(12345)

        assert result is True
        assert not User.objects.filter(telegram_uid=12345).exists()

    def test_delete_not_found(self):
        result = self.repo.delete(99999)
        assert result is False

    def test_exists_true(self):
        User.objects.create(telegram_uid=12345)

        assert self.repo.exists(12345) is True

    def test_exists_false(self):
        assert self.repo.exists(99999) is False

    def test_exists_even_deleted_flag(self):
        User.objects.create(telegram_uid=12345)

        # User model has no deleted_at field, so even_deleted=False
        # hits the FieldDoesNotExist branch and still returns True
        assert self.repo.exists(12345, even_deleted=False) is True

    def test_all_returns_entities(self):
        User.objects.create(telegram_uid=111, username="a")
        User.objects.create(telegram_uid=222, username="b")

        result = self.repo.all()

        assert len(result) == 2
        assert all(isinstance(e, UserEntity) for e in result)

    def test_all_empty(self):
        result = self.repo.all()
        assert result == []

    def test_all_even_deleted_false(self):
        User.objects.create(telegram_uid=111)

        # User has no deleted_at, hits FieldDoesNotExist → returns all
        result = self.repo.all(even_deleted=False)
        assert len(result) == 1


