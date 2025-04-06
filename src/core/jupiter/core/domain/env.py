"""An environment for a jupiter application."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class Env(EnumValue):
    """An environment for a jupiter application."""

    PRODUCTION = "production"  # Something a real life user is interacting with
    STAGING = "staging"  # Production-like environment for testing. Might be a nightly build, or some per-branch environment.
    LOCAL = "local"  # A local development environment.

    @property
    def is_development(self) -> bool:
        """Whether this is a development environment."""
        return self != Env.PRODUCTION

    @property
    def is_live(self) -> bool:
        """Whether this is a live environment."""
        return self == Env.PRODUCTION or self == Env.STAGING

    def __str__(self) -> str:
        """The string representation of the environment."""
        return self.value
