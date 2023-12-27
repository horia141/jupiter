"""A repository of smart lists."""
import abc

from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.framework.repository import (
    BranchEntityRepository,
)


class SmartListRepository(BranchEntityRepository[SmartList], abc.ABC):
    """A repository of smart lists."""
