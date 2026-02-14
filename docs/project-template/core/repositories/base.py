"""
Base repository with concrete CRUD operations.

Provides standard database operations that all repositories inherit.
Repositories work with Django models internally but return Pydantic entities.
"""
from typing import Any, Generic, Type, TypeVar

from asgiref.sync import sync_to_async
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from django.utils import timezone

from core.base_entity import BaseEntity

M = TypeVar("M", bound=Model)
E = TypeVar("E", bound=BaseEntity)


class BaseRepository(Generic[M, E]):
    """
    Base repository class providing standard CRUD operations.

    This class provides concrete implementations of common database operations.
    Subclasses only need to override methods if custom behavior is required.

    All methods return Pydantic entities, not Django models.
    """

    def __init__(self, model: Type[M], entity: Type[E], not_found_exception: Type[Exception]):
        """
        Initialize repository with model, entity, and exception types.

        Args:
            model: Django model class
            entity: Pydantic entity class
            not_found_exception: Exception to raise when entity not found
        """
        self.model = model
        self.entity = entity
        self.not_found_exception = not_found_exception

    def get(self, pk: Any) -> E:
        """
        Get entity by primary key.

        Args:
            pk: Primary key value

        Returns:
            Entity instance

        Raises:
            not_found_exception: If entity with given pk not found
        """
        try:
            model = self.model.objects.get(pk=pk)
            entity = self.entity.from_model(model)
            return entity
        except self.model.DoesNotExist:
            raise self.not_found_exception(f"{self.model.__name__} with id {pk} not found.")

    async def aget(self, pk: Any) -> E:
        """Async version: Get entity by primary key."""
        return await sync_to_async(self.get)(pk)

    def add(self, entity: E) -> E:
        """
        Add new entity to database.

        Args:
            entity: Entity instance to add

        Returns:
            Created entity with updated fields (e.g., auto-generated ID)
        """
        model = entity.to_model()
        model.save()
        return self.entity.from_model(model)

    async def aadd(self, entity: E) -> E:
        """Async version: Add new entity to database."""
        return await sync_to_async(self.add)(entity)

    def update(self, entity: E) -> E:
        """
        Update existing entity in database.

        Args:
            entity: Entity instance with updated data

        Returns:
            Updated entity instance
        """
        model = entity.to_model()
        model.save()
        return self.entity.from_model(model)

    async def aupdate(self, entity: E) -> E:
        """Async version: Update existing entity in database."""
        return await sync_to_async(self.update)(entity)

    def delete(self, pk: Any) -> bool:
        """
        Delete entity by primary key (soft delete if deleted_at field exists).

        Args:
            pk: Primary key value

        Returns:
            True if deleted, False if not found
        """
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
        """Async version: Delete entity by primary key."""
        return await sync_to_async(self.delete)(pk)

    def exists(self, pk: Any, even_deleted: bool = True) -> bool:
        """
        Check if entity exists by primary key.

        Args:
            pk: Primary key value
            even_deleted: If False, exclude soft-deleted entities (default: True)

        Returns:
            True if exists, False otherwise
        """
        if even_deleted:
            return self.model.objects.filter(pk=pk).exists()
        else:
            try:
                self.model._meta.get_field('deleted_at')
                return self.model.objects.filter(pk=pk, deleted_at=None).exists()
            except FieldDoesNotExist:
                return self.model.objects.filter(pk=pk).exists()

    async def aexists(self, pk: Any, even_deleted: bool = True) -> bool:
        """Async version: Check if entity exists by primary key."""
        return await sync_to_async(self.exists)(pk, even_deleted=even_deleted)

    def all(self, even_deleted: bool = True) -> list[E]:
        """
        Get all entities.

        Args:
            even_deleted: If False, exclude soft-deleted entities (default: True)

        Returns:
            List of all entity instances
        """
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
        """Async version: Get all entities."""
        return await sync_to_async(self.all)(even_deleted=even_deleted)
