"""A repository of smart lists."""
import abc

from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.framework.repository import (
    BranchEntityNotFoundError,
    BranchEntityRepository,
)


class SmartListNotFoundError(BranchEntityNotFoundError):
    """Error raised when a smart list is not found."""


class SmartListRepository(BranchEntityRepository[SmartList], abc.ABC):
    """A repository of smart lists."""
