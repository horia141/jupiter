"""Framework level elements for storage."""
import abc


class ConnectionPrepareError(Exception):
    """Raised when a connection fails to prepare."""


class Connection(abc.ABC):
    """A connection to a relational-like storage engine."""

    @abc.abstractmethod
    async def prepare(self) -> None:
        """Prepare the connection."""

    @abc.abstractmethod
    def nuke(self) -> None:
        """Completely destroy the storage this connection is linked with."""
