"""A repository of smart list entries."""
import abc
from typing import Optional, List, Iterable

from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class SmartListItemNotFoundError(LeafEntityNotFoundError):
    """Error raised when a smart list item is not found."""


class SmartListItemRepository(LeafEntityRepository[SmartListItem], abc.ABC):
    """A repository of smart list entries."""

    @abc.abstractmethod
    def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_is_done: Optional[bool] = None,
        filter_tag_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[SmartListItem]:
        """Find all smart list entries matching some criteria."""
