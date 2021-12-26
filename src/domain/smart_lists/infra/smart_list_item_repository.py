"""A repository of smart list entries."""
import abc
from typing import Optional, List, Iterable

from domain.smart_lists.smart_list_item import SmartListItem
from framework.base.entity_id import EntityId
from framework.storage import Repository


class SmartListItemNotFoundError(Exception):
    """Error raised when a smart list item is not found."""


class SmartListItemRepository(Repository, abc.ABC):
    """A repository of smart list entries."""

    @abc.abstractmethod
    def create(self, smart_list_item: SmartListItem) -> SmartListItem:
        """Create a smart list item."""

    @abc.abstractmethod
    def save(self, smart_list_item: SmartListItem) -> SmartListItem:
        """Save a smart list item - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListItem:
        """Load a given smart list item."""

    @abc.abstractmethod
    def find_all_for_smart_list(self, smart_list_ref_id: EntityId, allow_archived: bool = False) -> List[SmartListItem]:
        """Retrieve all smart list entries for a given smart list."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_is_done: Optional[bool] = None,
            filter_tag_ref_ids: Optional[Iterable[EntityId]] = None) -> List[SmartListItem]:
        """Find all smart list entries matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> SmartListItem:
        """Hard remove a smart list - an irreversible operation."""
