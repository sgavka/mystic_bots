from typing import Optional

from asgiref.sync import sync_to_async

from core.entities import UserEntity
from core.exceptions import UserNotFoundException
from core.models import User
from core.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserEntity]):
    def __init__(self):
        super().__init__(
            model=User,
            entity=UserEntity,
            not_found_exception=UserNotFoundException,
        )

    def get_or_create(self, telegram_uid: int, defaults: dict) -> tuple[UserEntity, bool]:
        user, created = User.objects.get_or_create(
            telegram_uid=telegram_uid,
            defaults=defaults,
        )
        return UserEntity.from_model(user), created

    async def aget_or_create(self, telegram_uid: int, defaults: dict) -> tuple[UserEntity, bool]:
        return await sync_to_async(self.get_or_create)(telegram_uid, defaults)

    def update_by_pk(self, telegram_uid: int, **data) -> Optional[UserEntity]:
        try:
            user = User.objects.get(telegram_uid=telegram_uid)
            for key, value in data.items():
                setattr(user, key, value)
            user.save()
            return UserEntity.from_model(user)
        except User.DoesNotExist:
            return None

    async def aupdate_by_pk(self, telegram_uid: int, **data) -> Optional[UserEntity]:
        return await sync_to_async(self.update_by_pk)(telegram_uid, **data)

    def update_or_create(self, telegram_uid: int, defaults: dict) -> tuple[UserEntity, bool]:
        user, created = User.objects.update_or_create(
            telegram_uid=telegram_uid,
            defaults=defaults,
        )
        return UserEntity.from_model(user), created

    async def aupdate_or_create(self, telegram_uid: int, defaults: dict) -> tuple[UserEntity, bool]:
        return await sync_to_async(self.update_or_create)(telegram_uid, defaults)
