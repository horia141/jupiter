"""Helpers for working with optional types."""

from types import UnionType
from typing import Any, Union, get_args, get_origin


def normalize_optional(the_type: type[Any]) -> tuple[type[Any], bool]:  # type: ignore
    """Normalize the optional type.""" ""
    if (orgin_type := get_origin(the_type)) is not None:
        if orgin_type is Union or (
            isinstance(orgin_type, type) and issubclass(orgin_type, UnionType)
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
