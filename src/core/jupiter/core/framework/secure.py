"""Annotations for codepaths that deal with security in some way."""
from typing import Callable, TypeVar

X = TypeVar("X")


def secure_fn(f: Callable[..., X]) -> Callable[..., X]:  # type: ignore
    """Mark this function as dealing with security, auth, etc but it's noop otherwise."""
    return f


def secure_class(cls: type[X]) -> type[X]:
    """Mark this class as dealing with security, auth, etc but it's noop otherwise."""
    return cls
