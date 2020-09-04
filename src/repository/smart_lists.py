"""Repository for smart lists."""
import logging
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Iterable
import typing

from models.basic import EntityId, Timestamp

LOGGER = logging.getLogger(__name__)


@dataclass()
class SmartList:
    """A container for smart list items."""
    ref_id: EntityId
    name: str
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Timestamp


class SmartListsRepository:
    """A repository for lists."""

    def __enter__(self) -> 'SmartListsRepository':
        """Enter context."""
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_smart_list(self) -> SmartList:
        """Create a list."""

    def archive_smart_list(self) -> SmartList:
        """Archive a list."""

    def load_all_smart_lists(self) -> Iterable[SmartList]:
        """Load all lists."""

    def load_smart_list(self) -> SmartList:
        """Load a particular list by its id."""

    def save_smart_list(self) -> SmartList:
        """Store a particular list."""


@dataclass()
class SmartListItem:
    """An item in a smart list."""

    ref_id: EntityId
    smart_list_ref_id: EntityId
    name: str
    url: Optional[str]
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Timestamp


class SmartListItemsRepository:
    """A repository for smart list items."""

    def __enter__(self) -> 'SmartListItemsRepository':
        """Enter context."""
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_smart_list_item(self) -> SmartListItem:
        """Create a list item."""

    def archive_smart_list_item(self) -> SmartListItem:
        """Archive a list item."""

    def load_all_smart_list_items(self) -> Iterable[SmartList]:
        """Load all lists items."""

    def load_smart_list_item(self) -> SmartList:
        """Load a particular list item by its id."""

    def save_smart_list_item(self) -> SmartList:
        """Store a particular list item."""

    def hard_remove_smart_list_item(self) -> SmartListItem:
        """Hard remove a list item."""
