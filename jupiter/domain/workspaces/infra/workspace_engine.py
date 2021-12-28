"""A unit of work for workspaces."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository
from jupiter.framework.storage import UnitOfWork, Engine


class WorkspaceUnitOfWork(UnitOfWork, abc.ABC):
    """A person specialized unit of work."""

    @property
    @abc.abstractmethod
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace database repository."""


class WorkspaceEngine(Engine[WorkspaceUnitOfWork], abc.ABC):
    """The person engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[WorkspaceUnitOfWork]:
        """Build a unit of work."""
