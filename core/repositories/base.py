from typing import Any, Generic, Type, TypeVar

from asgiref.sync import sync_to_async
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from django.utils import timezone

from core.base_entity import BaseEntity

M = TypeVar("M", bound=Model)
E = TypeVar("E", bound=BaseEntity)


class BaseRepository(Generic[M, E]):
    def __init__(self, model: Type[M], entity: Type[E], not_found_exception: Type[Exception]):
        self.model = model
        self.entity = entity
        self.not_found_exception = not_found_exception

    def get(self, pk: Any) -> E:
        try:
            model = self.model.objects.get(pk=pk)
            return self.entity.from_model(model)
        except self.model.DoesNotExist:
            raise self.not_found_exception(f"{self.model.__name__} with id {pk} not found.")

    async def aget(self, pk: Any) -> E:
        return await sync_to_async(self.get)(pk)

    def add(self, entity: E) -> E:
        model = entity.to_model()
        model.save()
        return self.entity.from_model(model)

    async def aadd(self, entity: E) -> E:
        return await sync_to_async(self.add)(entity)

    def update(self, entity: E) -> E:
        model = entity.to_model()
        model.save()
        return self.entity.from_model(model)

    async def aupdate(self, entity: E) -> E:
        return await sync_to_async(self.update)(entity)

    def delete(self, pk: Any) -> bool:
        try:
            self.model._meta.get_field('deleted_at')
            instances = self.model.objects.filter(pk=pk)
            count = instances.update(deleted_at=timezone.now())
            return count == 1
        except FieldDoesNotExist:
            instances = self.model.objects.filter(pk=pk)
            deleted_count, _ = instances.delete()
            return deleted_count == 1

    async def adelete(self, pk: Any) -> bool:
        return await sync_to_async(self.delete)(pk)

    def exists(self, pk: Any, even_deleted: bool = True) -> bool:
        if even_deleted:
            return self.model.objects.filter(pk=pk).exists()
        else:
            try:
                self.model._meta.get_field('deleted_at')
                return self.model.objects.filter(pk=pk, deleted_at=None).exists()
            except FieldDoesNotExist:
                return self.model.objects.filter(pk=pk).exists()

    async def aexists(self, pk: Any, even_deleted: bool = True) -> bool:
        return await sync_to_async(self.exists)(pk, even_deleted=even_deleted)

    def all(self, even_deleted: bool = True) -> list[E]:
        if even_deleted:
            models = self.model.objects.all()
        else:
            try:
                self.model._meta.get_field('deleted_at')
                models = self.model.objects.filter(deleted_at=None)
            except FieldDoesNotExist:
                models = self.model.objects.all()
        return [self.entity.from_model(model) for model in models]

    async def aall(self, even_deleted: bool = True) -> list[E]:
        return await sync_to_async(self.all)(even_deleted=even_deleted)
