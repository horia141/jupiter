"""A repository of smart list tags."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class SmartListTagRepository(LeafEntityRepository[SmartListTag], abc.ABC):
    """A repository of smart list tags."""
