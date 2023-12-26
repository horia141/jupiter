"""Helpers for working with JSON at the type level."""
import dataclasses
import typing
import uuid
from enum import Enum
from typing import Any, Dict, List, Union

from jupiter.core.framework.value import SecretValue, Value
from pendulum.date import Date
from pendulum.datetime import DateTime

JSONValueType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]  # type: ignore
JSONDictType = Dict[str, JSONValueType]


def process_primitive_to_json_key(primitive: int | float | str | object) -> str:
    """Transform a primitive-ish type to a JSON object key."""
    if isinstance(primitive, int):
        return str(primitive)
    elif isinstance(primitive, float):
        return str(primitive)
    elif isinstance(primitive, str):
        return primitive
    elif isinstance(primitive, Date):
        return str(primitive)
    elif isinstance(primitive, DateTime):
        return str(primitive)
    elif isinstance(primitive, Enum):
        return str(primitive.value)
    elif isinstance(primitive, SecretValue):
        return f"Redacted {str(primitive)}"
    elif isinstance(primitive, Value):
        return str(primitive)  # A bit of a hack really!
    elif isinstance(primitive, uuid.UUID):
        return str(primitive)
    else:
        raise Exception(
            f"Invalid type for key of type {primitive.__class__.__name__}",
        )


def process_primitive_to_json(
    primitive: typing.Union[None, int, float, str, object],
    key: str | None = None,
) -> JSONValueType:
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
    elif isinstance(primitive, SecretValue):
        return f"Redacted {str(primitive)}"
    elif isinstance(primitive, Value):
        return str(primitive)  # A bit of a hack really!
    elif "Entity" in [t.__name__ for t in type(primitive).__mro__]:
        return {
            "ref_id": str(getattr(primitive, "ref_id")),  # noqa: B009
            "aggregate-root-type": primitive.__class__.__name__,
        }
    elif isinstance(primitive, uuid.UUID):
        return str(primitive)
    elif dataclasses.is_dataclass(primitive) and not isinstance(primitive, type):
        return {
            k: process_primitive_to_json(v, k)
            for k, v in dataclasses.asdict(primitive).items()
        }
    elif isinstance(primitive, list):
        return [process_primitive_to_json(p, key) for p in primitive]
    elif isinstance(primitive, dict):
        return {
            process_primitive_to_json_key(k): process_primitive_to_json(v, k)
            for k, v in primitive.items()
        }
    elif isinstance(primitive, frozenset):
        return [process_primitive_to_json(p, key) for p in primitive]
    elif isinstance(primitive, set):
        return [process_primitive_to_json(p, key) for p in primitive]
    else:
        raise Exception(
            f"Invalid type for event field {key if key else 'root'} of type {primitive.__class__.__name__}",
        )
