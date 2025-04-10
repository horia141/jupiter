"""Use case classes and decorators for defining use case inputs and outputs."""

from dataclasses import dataclass
from typing import TypeVar

from typing_extensions import dataclass_transform


@dataclass(frozen=True)
class UseCaseIOBase:
    """The base class for use case inputs and output types."""


@dataclass(frozen=True)
class UseCaseArgsBase(UseCaseIOBase):
    """The base class for use case args types."""


_UseCaseArgsT = TypeVar("_UseCaseArgsT", bound=UseCaseArgsBase)


@dataclass_transform(frozen_default=True)
def use_case_args(cls: type[_UseCaseArgsT]) -> type[_UseCaseArgsT]:
    """A decorator for use case args types."""
    return dataclass(frozen=True)(cls)


@dataclass(frozen=True)
class UseCaseResultBase(UseCaseIOBase):
    """The base class for use case args results."""


_UseCaseResultT = TypeVar("_UseCaseResultT", bound=UseCaseResultBase)


@dataclass_transform(frozen_default=True)
def use_case_result(cls: type[_UseCaseResultT]) -> type[_UseCaseResultT]:
    """A decorator for use case result types."""
    return dataclass(frozen=True)(cls)


@dataclass_transform(frozen_default=True)
def use_case_result_part(cls: type[_UseCaseResultT]) -> type[_UseCaseResultT]:
    """A decorator for use case result part types."""
    return dataclass(frozen=True)(cls)
