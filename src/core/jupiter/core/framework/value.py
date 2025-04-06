"""Framework level elements for value object."""

import enum
from dataclasses import dataclass
from typing import Generic, TypeVar, cast, get_args

from jupiter.core.framework.concept import Concept
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.secure import secure_class
from typing_extensions import dataclass_transform


class Value(Concept):
    """A value object in the domain."""


_ValueT = TypeVar("_ValueT", bound="AtomicValue[Primitive] | CompositeValue")


@dataclass_transform(frozen_default=True)
def value(cls: type[_ValueT]) -> type[_ValueT]:
    """A value object in the domain."""
    return dataclass(frozen=True)(cls)


@dataclass_transform(frozen_default=True)
def hashable_value(cls: type[_ValueT]) -> type[_ValueT]:
    """A value object in the domain that is hashable."""
    return dataclass(eq=True, unsafe_hash=True, frozen=True)(cls)


_PrimitiveT_co = TypeVar("_PrimitiveT_co", bound=Primitive, covariant=True)

_AtomicValueT = TypeVar("_AtomicValueT", bound="AtomicValue[Primitive]")


@dataclass(frozen=True)
class AtomicValue(
    Generic[_PrimitiveT_co],
    Value,
):
    """An atomic value object in the domain."""

    @classmethod
    def base_type_hack(cls: type[_AtomicValueT]) -> type[_PrimitiveT_co]:
        """Get the base type of this value."""
        return cast(type[_PrimitiveT_co], get_args(cls.__orig_bases__[0])[0])  # type: ignore[attr-defined]

    def _validate(self) -> None:
        """Validate this value."""

    def __post_init__(self) -> None:
        """Post init hook."""
        self._validate()


@dataclass(frozen=True)
class CompositeValue(Value):
    """An composite value object in the domain."""

    def _validate(self) -> None:
        """Validate this value."""

    def __post_init__(self) -> None:
        """Post init hook."""
        self._validate()


@enum.unique
class EnumValue(Value, enum.Enum):
    """A value that is also an enum."""

    @classmethod
    def get_all_values(cls: type["EnumValue"]) -> list[str]:
        """Get all the values for this enum."""
        return list(s.value for s in cls)


_EnumValueT = TypeVar("_EnumValueT", bound=EnumValue)


def enum_value(cls: type[_EnumValueT]) -> type[_EnumValueT]:
    """A value object in the domain that is also an enum."""
    return cls


@dataclass(repr=False, frozen=True)
@secure_class
class SecretValue(Value):
    """A secret value object in the domain."""

    def __repr__(self) -> str:
        """Get a string representation of this value."""
        # Just a very silly protection. Even if someone tries to print or store this they'll get
        # some ugly text like this.
        return f'{self.__class__.__name__}("****************")'

    def __str__(self) -> str:
        """Get a string representation of this value."""
        # Just a very silly protection. Even if someone tries to print or store this they'll get
        # some ugly text like this.
        return "****************"


_SecretValueT = TypeVar("_SecretValueT", bound=SecretValue)


@dataclass_transform(frozen_default=True)
def secret_value(cls: type[_SecretValueT]) -> type[_SecretValueT]:
    """A value object in the domain that is also a secret."""
    return dataclass(repr=False, frozen=True)(secure_class(cls))
