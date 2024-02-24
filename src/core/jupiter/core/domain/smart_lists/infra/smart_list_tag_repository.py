"""A repository of smart list tags."""
import abc

from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class SmartListTagRepository(LeafEntityRepository[SmartListTag], abc.ABC):
    """A repository of smart list tags."""
