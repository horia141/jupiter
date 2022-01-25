"""Helpers for working with JSON at the type level."""
import dataclasses
import typing
import uuid
from enum import Enum
from typing import List, Union, Dict, Any

from pendulum import Date, DateTime

from jupiter.framework.value import Value

JSONValueType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]  # type: ignore
JSONDictType = Dict[str, JSONValueType]


def process_primitive_to_json(primitive: typing.Union[None, int, float, str, object], key: str) -> JSONValueType:
    """Transform a primitive-ish type to a JSON serializable object."""
    if primitive is None:
        return primitive
    elif isinstance(primitive, int):
        return primitive
    elif isinstance(primitive, float):
        return primitive
    elif isinstance(primitive, str):
        return primitive
    elif isinstance(primitive, Date):
        return str(primitive)
    elif isinstance(primitive, DateTime):
        return str(primitive)
    elif isinstance(primitive, Enum):
        return process_primitive_to_json(primitive.value, key)
    elif isinstance(primitive, Value):
        return str(primitive)  # A bit of a hack really!
    elif isinstance(primitive, uuid.UUID):
        return str(primitive)
    elif dataclasses.is_dataclass(primitive):
        return {k: process_primitive_to_json(v, k) for k, v in dataclasses.asdict(primitive).items()}
    elif isinstance(primitive, list):
        return [process_primitive_to_json(p, key) for p in primitive]
    elif isinstance(primitive, dict):
        return {k: process_primitive_to_json(v, k) for k, v in primitive.items()}
    elif isinstance(primitive, frozenset):
        return [process_primitive_to_json(p, key) for p in primitive]
    elif isinstance(primitive, set):
        return [process_primitive_to_json(p, key) for p in primitive]
    else:
        raise Exception(f"Invalid type for event field {key} of type {primitive.__class__.__name__}")
