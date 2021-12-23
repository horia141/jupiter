"""A unit of work for smart lists."""
import abc
from contextlib import contextmanager
from typing import Iterator

from domain.smart_lists.infra.smart_list_item_repository import SmartListItemRepository
from domain.smart_lists.infra.smart_list_repository import SmartListRepository
from domain.smart_lists.infra.smart_list_tag_repository import SmartListTagRepository
from framework.storage import UnitOfWork, Engine


class SmartListUnitOfWork(UnitOfWork, abc.ABC):
    """A smart list specialized unit of work."""

    @property
    @abc.abstractmethod
    def smart_list_repository(self) -> SmartListRepository:
        """The smart list repository."""

    @property
    @abc.abstractmethod
    def smart_list_tag_repository(self) -> SmartListTagRepository:
        """The smart list tag repository."""

    @property
    @abc.abstractmethod
    def smart_list_item_repository(self) -> SmartListItemRepository:
        """The smart list item repository."""


class SmartListEngine(Engine[SmartListUnitOfWork], abc.ABC):
    """The smart list engine."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[SmartListUnitOfWork]:
        """Build a unit of work."""
