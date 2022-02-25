"""A repository of smart list tags."""
import abc
from typing import Optional, List, Iterable

from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class SmartListTagNotFoundError(Exception):
    """Error raised when a smart list tag is not found."""


class SmartListTagRepository(Repository, abc.ABC):
    """A repository of smart list tags."""

    @abc.abstractmethod
    def create(self, smart_list_tag: SmartListTag) -> SmartListTag:
        """Create a smart list tag."""

    @abc.abstractmethod
    def save(self, smart_list_tag: SmartListTag) -> SmartListTag:
        """Save a smart list tag - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListTag:
        """Load a given smart list tag."""

    @abc.abstractmethod
    def find_all(
            self,
            smart_list_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_tag_names: Optional[Iterable[SmartListTagName]] = None) -> List[SmartListTag]:
        """Retrieve all smart list tags for a given smart list."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> SmartListTag:
        """Hard remove a smart list - an irreversible operation."""
