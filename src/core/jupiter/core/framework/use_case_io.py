from dataclasses import dataclass
from typing import TypeVar

from typing_extensions import dataclass_transform


@dataclass
class UseCaseIOBase:
    """The base class for use case inputs and output types."""


@dataclass
class UseCaseArgsBase(UseCaseIOBase):
    """The base class for use case args types."""


_UseCaseArgsT = TypeVar("_UseCaseArgsT", bound=UseCaseArgsBase)


@dataclass_transform()
def use_case_args(cls: type[_UseCaseArgsT]) -> type[_UseCaseArgsT]:
    return dataclass(cls)


@dataclass
class UseCaseResultBase(UseCaseIOBase):
    """The base class for use case args results."""


_UseCaseResultT = TypeVar("_UseCaseResultT", bound=UseCaseResultBase)


@dataclass_transform()
def use_case_result(cls: type[_UseCaseResultT]) -> type[_UseCaseResultT]:
    return dataclass(cls)


@dataclass_transform()
def use_case_result_part(cls: type[_UseCaseResultT]) -> type[_UseCaseResultT]:
    return dataclass(cls)
