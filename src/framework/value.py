"""Framework level elements for value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Value:
    """A value object in the domain."""
