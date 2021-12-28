"""A unit of work for recurring tasks."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.domain.recurring_tasks.infra.recurring_task_collection_repository import RecurringTaskCollectionRepository
from jupiter.domain.recurring_tasks.infra.recurring_task_repository import RecurringTaskRepository
from jupiter.framework.storage import UnitOfWork, Engine


class RecurringTaskUnitOfWork(UnitOfWork, abc.ABC):
    """A recurring tasks specialised unit of work."""

    @property
    @abc.abstractmethod
    def recurring_task_collection_repository(self) -> RecurringTaskCollectionRepository:
        """The recurring task collection repository."""

    @property
    @abc.abstractmethod
    def recurring_task_repository(self) -> RecurringTaskRepository:
        """The recurring task repository."""


class RecurringTaskEngine(Engine[RecurringTaskUnitOfWork], abc.ABC):
    """The recurring task engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[RecurringTaskUnitOfWork]:
        """Build a unit of work."""
