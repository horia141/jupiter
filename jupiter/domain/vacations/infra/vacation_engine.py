"""A unit of work for vacations."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.framework.storage import UnitOfWork, Engine


class VacationUnitOfWork(UnitOfWork, abc.ABC):
    """A vacation specialized unit of work."""

    @property
    @abc.abstractmethod
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""


class VacationEngine(Engine[VacationUnitOfWork], abc.ABC):
    """The vacation engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[VacationUnitOfWork]:
        """Build a unit of work."""
