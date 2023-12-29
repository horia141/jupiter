"""A repository of smart list tags."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class SmartListTagRepository(LeafEntityRepository[SmartListTag], abc.ABC):
    """A repository of smart list tags."""

    @abc.abstractmethod
    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_tag_names: Optional[Iterable[SmartListTagName]] = None,
    ) -> List[SmartListTag]:
        """Retrieve all smart list tags for a given smart list."""
