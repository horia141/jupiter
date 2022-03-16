"""A repository of smart lists."""
import abc

from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.framework.repository import BranchEntityRepository, BranchEntityAlreadyExistsError,\
    BranchEntityNotFoundError


class SmartListAlreadyExistsError(BranchEntityAlreadyExistsError):
    """Error raised when a smart list with the given key already exists."""


class SmartListNotFoundError(BranchEntityNotFoundError):
    """Error raised when a smart list is not found."""


class SmartListRepository(BranchEntityRepository[SmartListKey, SmartList], abc.ABC):
    """A repository of smart lists."""
