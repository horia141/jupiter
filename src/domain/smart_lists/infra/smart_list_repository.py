"""A repository of smart lists."""
import abc
from typing import Optional, List, Iterable

from domain.smart_lists.smart_list import SmartList
from models.basic import SmartListKey
from models.framework import Repository, EntityId


class SmartListRepository(Repository, abc.ABC):
    """A repository of smart lists."""

    @abc.abstractmethod
    def create(self, smart_list: SmartList) -> SmartList:
        """Create a smart list."""

    @abc.abstractmethod
    def save(self, smart_list: SmartList) -> SmartList:
        """Save a smart list - it should already exist."""

    @abc.abstractmethod
    def get_by_key(self, key: SmartListKey) -> SmartList:
        """Find a smart list by key."""

    @abc.abstractmethod
    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartList:
        """Find a smart list by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> List[SmartList]:
        """Find all smart lists matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> SmartList:
        """Hard remove a smart list - an irreversible operation."""
