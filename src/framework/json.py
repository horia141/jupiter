"""Helpers for working with JSON at the type level."""
from typing import List, Union, Dict, Any

JSONValueType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]  # type: ignore
JSONDictType = Dict[str, JSONValueType]
