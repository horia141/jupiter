"""The type of hosting Jupiter is run into."""
import enum


@enum.unique
class Hosting(enum.Enum):
    """The type of hosting Jupiter is run into."""

    HOSTED_GLOBAL = "hosted-global"
    LOCAL = "local"
