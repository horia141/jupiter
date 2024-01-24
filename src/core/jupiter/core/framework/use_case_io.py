from typing import TypeVar
from typing_extensions import dataclass_transform
from jupiter.core.framework.json import JSONDictType, process_primitive_to_json
from jupiter.core.framework.update_action import UpdateAction


from dataclasses import dataclass, fields


@dataclass
class UseCaseIOBase:
    """The base class for use case inputs and output types."""

    def to_serializable_dict(self) -> JSONDictType:
        """Transform this argument set to a JSON compatible representation."""
        serialized_form = {}
        for field in fields(self):
            field_value = getattr(self, field.name)
            if isinstance(field_value, UpdateAction):
                if field_value.should_change:
                    serialized_form[field.name] = process_primitive_to_json(
                        field_value.just_the_value,
                        field.name,
                    )
            else:
                serialized_form[field.name] = process_primitive_to_json(
                    field_value,
                    field.name,
                )
        return serialized_form


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
def use_case_result_part(cls: type[object]) -> type[object]:
    return dataclass(cls)