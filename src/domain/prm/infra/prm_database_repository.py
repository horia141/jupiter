"""A repository of PRM databases."""
import abc

from domain.prm.prm_database import PrmDatabase
from framework.storage import Repository


class PrmDatabaseAlreadyExistsError(Exception):
    """Error raised when a PRM database already exists."""


class PrmDatabaseNotFoundError(Exception):
    """Error raised when the PRM database is not found."""


class PrmDatabaseRepository(Repository, abc.ABC):
    """A repository of PRM databases."""

    @abc.abstractmethod
    def create(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Create a PRM database."""

    @abc.abstractmethod
    def save(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Save a PRM database - it should already exist."""

    @abc.abstractmethod
    def load(self) -> PrmDatabase:
        """Load the PRM database."""
