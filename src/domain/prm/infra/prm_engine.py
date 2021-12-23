"""A unit of work for person."""
import abc
from contextlib import contextmanager
from typing import Iterator

from domain.prm.infra.person_repository import PersonRepository
from domain.prm.infra.prm_database_repository import PrmDatabaseRepository
from framework.storage import UnitOfWork, Engine


class PrmUnitOfWork(UnitOfWork, abc.ABC):
    """A person specialized unit of work."""

    @property
    @abc.abstractmethod
    def prm_database_repository(self) -> PrmDatabaseRepository:
        """The PRM database repository."""

    @property
    @abc.abstractmethod
    def person_repository(self) -> PersonRepository:
        """The person repository."""


class PrmEngine(Engine[PrmUnitOfWork], abc.ABC):
    """The person engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[PrmUnitOfWork]:
        """Build a unit of work."""
