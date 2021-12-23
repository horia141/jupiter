"""Framework level elements for storage."""
import abc
from contextlib import contextmanager
from typing import TypeVar, Generic, Iterator


class Repository(abc.ABC):
    """A repository."""


UnitOfWorkType = TypeVar('UnitOfWorkType', bound='UnitOfWork')


class UnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""


class Engine(Generic[UnitOfWorkType], abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[UnitOfWorkType]:
        """Build a unit of work."""
