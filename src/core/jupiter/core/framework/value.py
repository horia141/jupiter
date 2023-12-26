"""Framework level elements for value object."""
import enum
from dataclasses import dataclass
from typing import TypeVar

from jupiter.core.framework.secure import secure_class
from typing_extensions import dataclass_transform


@dataclass
class Value:
    """A value object in the domain."""


_ValueT = TypeVar("_ValueT", bound="Value")


@dataclass_transform()
def value(cls: type[_ValueT]) -> type[_ValueT]:
    return dataclass(cls)


@dataclass_transform()
def hashable_value(cls: type[_ValueT]) -> type[_ValueT]:
    return dataclass(eq=True, unsafe_hash=True)(cls)


@enum.unique
class EnumValue(enum.Enum):
    """A value that is also an enum."""


_EnumValueT = TypeVar("_EnumValueT", bound=EnumValue)


def enum_value(cls: type[_EnumValueT]) -> type[_EnumValueT]:
    return cls


@dataclass(repr=False)
@secure_class
class SecretValue(Value):
    """A secret value object in the domain."""

    def __repr__(self) -> str:
        """Get a string representation of this value."""
        # Just a very silly protection. Even if someone tries to print or store this they'll get
        # some ugly text like this.
        return "****************"

    def __str__(self) -> str:
        """Get a string representation of this value."""
        # Just a very silly protection. Even if someone tries to print or store this they'll get
        # some ugly text like this.
        return "****************"


_SecretValueT = TypeVar("_SecretValueT", bound=SecretValue)


@dataclass_transform()
def secret_value(cls: type[_SecretValueT]) -> type[_SecretValueT]:
    return dataclass(repr=False)(secure_class(cls))
