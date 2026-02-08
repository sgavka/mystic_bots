from typing import List, NoReturn, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T", bound="BaseEntity")


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls: type[T], model) -> T:
        return cls.model_validate(model)

    @classmethod
    def from_models(cls: type[T], models: List) -> List[T]:
        return [cls.from_model(model) for model in models]

    def to_model(self) -> NoReturn:
        raise NotImplementedError("to_model() must be implemented in subclass")
