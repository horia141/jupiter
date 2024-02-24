"""A repository of smart list entries."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class SmartListItemRepository(LeafEntityRepository[SmartListItem], abc.ABC):
    """A repository of smart list entries."""
