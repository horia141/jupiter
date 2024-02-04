"""Some utilities."""
import importlib
import pkgutil
from datetime import date, datetime
from types import ModuleType
from typing import Any, TypeGuard, get_origin

from jupiter.core.framework.entity import Entity
from jupiter.core.framework.record import Record
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.use_case_io import UseCaseArgsBase
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
            ),
        )
    )
