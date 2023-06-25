"""Framework level element for a value that isn't supposed to be printed willy-nilly."""

from dataclasses import dataclass

from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.value import Value


@dataclass(repr=False)
@secure_class
class SecretValue(Value):
    """A secret value object in the domain."""

    def __repr__(self) -> str:
        """Get a string representation of this value."""
        # Just a very silly protection. Even if someone tries to print or store this they'll get
        # some ugly text like this.
        return "****************"

    def __str__(self) -> str:
        """Get a string representation of this value."""
        # Just a very silly protection. Even if someone tries to print or store this they'll get
        # some ugly text like this.
        return "****************"
