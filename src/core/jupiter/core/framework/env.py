"""An environment for a Jupiter application."""


import enum


@enum.unique
class Env(enum.Enum):
    """An environment for a Jupiter application."""

    PRODUCTION = "production"  # Something a real life user is interacting with
    STAGING = "staging"  # Production-like environment for testing. Might be a nightly build, or some per-branch environment.
    LOCAL = "local"  # A local development environment.

    @property
    def is_development(self) -> bool:
        """Whether this is a development environment."""
        return self != Env.PRODUCTION
