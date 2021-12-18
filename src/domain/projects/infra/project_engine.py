"""A unit of work for projects."""
import abc
from contextlib import contextmanager
from typing import Iterator

from domain.projects.infra.project_repository import ProjectRepository
from models.framework import UnitOfWork, Engine


class ProjectUnitOfWork(UnitOfWork, abc.ABC):
    """A person specialized unit of work."""

    @property
    @abc.abstractmethod
    def project_repository(self) -> ProjectRepository:
        """The project database repository."""


class ProjectEngine(Engine[ProjectUnitOfWork], abc.ABC):
    """The person engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[ProjectUnitOfWork]:
        """Build a unit of work."""
