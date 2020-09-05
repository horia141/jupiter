"""Repository for smart lists."""
import logging
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Iterable
import typing

from models.basic import EntityId, Timestamp

LOGGER = logging.getLogger(__name__)


@dataclass()
class SmartListRow:
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

    def create_smart_list(self, name: str) -> SmartListRow:
        """Create a list."""

    def archive_smart_list(self) -> SmartListRow:
        """Archive a list."""

    def load_all_smart_lists(self) -> Iterable[SmartListRow]:
        """Load all lists."""

    def load_smart_list(self) -> SmartListRow:
        """Load a particular list by its id."""

    def save_smart_list(self) -> SmartListRow:
        """Store a particular list."""


@dataclass()
class SmartListItemRow:
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

    def create_smart_list_item(self) -> SmartListItemRow:
        """Create a list item."""

    def archive_smart_list_item(self) -> SmartListItemRow:
        """Archive a list item."""

    def load_all_smart_list_items(self) -> Iterable[SmartListRow]:
        """Load all lists items."""

    def load_smart_list_item(self) -> SmartListRow:
        """Load a particular list item by its id."""

    def save_smart_list_item(self) -> SmartListRow:
        """Store a particular list item."""

    def hard_remove_smart_list_item(self) -> SmartListItemRow:
        """Hard remove a list item."""
