"""Some utilities."""
import importlib
import pkgutil
from datetime import date, datetime
from types import ModuleType, UnionType
from typing import Any, TypeGuard, Union, get_args, get_origin

from jupiter.core.framework.entity import Entity
from jupiter.core.framework.record import Record
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
    SecretValue,
)
from pendulum.date import Date
from pendulum.datetime import DateTime


def find_all_modules(
    *module_roots: ModuleType,
) -> list[ModuleType]:
    all_modules = []

    def explore_module_tree(the_module: ModuleType) -> None:
        for _, name, is_pkg in pkgutil.iter_modules(the_module.__path__):
            full_name = the_module.__name__ + "." + name
            all_modules.append(importlib.import_module(full_name))
            if is_pkg:
                submodule = getattr(the_module, name)
                explore_module_tree(submodule)

    for mr in module_roots:
        explore_module_tree(mr)
    return all_modules


def is_thing_ish_type(  # type: ignore
    the_type: type[Any],
) -> TypeGuard[type[Thing]]:
    return the_type in (
        type(None),
        bool,
        int,
        float,
        str,
        date,
        datetime,
        Date,
        DateTime,
    ) or (
        isinstance(the_type, type)
        and get_origin(the_type) is None
        and issubclass(
            the_type,
            (
                AtomicValue,
                CompositeValue,
                EnumValue,
                SecretValue,
                Entity,
                Record,
                UseCaseArgsBase,
                UseCaseResultBase
            ),
        )
    )

def normalize_optional(the_type: type[Any]) -> tuple[type[Any], bool]:  # type: ignore
    if (orgin_type := get_origin(the_type)) is not None:
        if orgin_type is Union or (
            isinstance(orgin_type, type)
            and issubclass(orgin_type, UnionType)
        ):
            field_args = get_args(the_type)

            if len(field_args) == 2:
                if field_args[0] is type(None):
                    return field_args[1], True
                elif field_args[1] is type(None):
                    return field_args[0], True
                else:
                    return the_type, False

            return the_type, False

        return the_type, False

    return the_type, False
