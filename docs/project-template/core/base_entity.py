"""
Base entity class for all Pydantic entities.

This module provides a base class for all entity classes in the application.
Entities are Pydantic models that decouple business logic from Django ORM models.
"""
from typing import List, NoReturn, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T", bound="BaseEntity")


class BaseEntity(BaseModel):
    """
    Base class for all entity classes.

    Provides common functionality like:
    - from_model() class method for converting Django models to entities
    - from_models() class method for converting lists of Django models
    - to_model() method for converting entities back to Django models (if needed)

    All entity classes should inherit from this class.
    """

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls: type[T], model) -> T:
        """
        Create entity from Django model instance.

        Args:
            model: Django model instance

        Returns:
            Entity instance populated with model data
        """
        return cls.model_validate(model)

    @classmethod
    def from_models(cls: type[T], models: List) -> List[T]:
        """
        Create list of entities from list of Django model instances.

        Args:
            models: List of Django model instances

        Returns:
            List of entity instances
        """
        return [cls.from_model(model) for model in models]

    def to_model(self) -> NoReturn:
        """
        Convert entity to Django model instance.

        This method should be overridden in subclasses if needed.
        Default implementation raises NotImplementedError.

        Returns:
            Django model instance

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError("to_model() must be implemented in subclass")
