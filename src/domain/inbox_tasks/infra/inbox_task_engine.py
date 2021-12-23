"""A unit of work for inbox tasks."""
import abc
from contextlib import contextmanager
from typing import Iterator

from domain.inbox_tasks.infra.inbox_task_collection_repository import InboxTaskCollectionRepository
from domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository
from framework.storage import UnitOfWork, Engine


class InboxTaskUnitOfWork(UnitOfWork, abc.ABC):
    """A inbox tasks specialised unit of work."""

    @property
    @abc.abstractmethod
    def inbox_task_collection_repository(self) -> InboxTaskCollectionRepository:
        """The inbox task collection repository."""

    @property
    @abc.abstractmethod
    def inbox_task_repository(self) -> InboxTaskRepository:
        """The inbox task repository."""


class InboxTaskEngine(Engine[InboxTaskUnitOfWork], abc.ABC):
    """The inbox task engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[InboxTaskUnitOfWork]:
        """Build a unit of work."""
