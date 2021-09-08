"""A manager of Notion-side smart lists."""
import abc
from typing import Iterable

from domain.smart_lists.smart_list import SmartList
from domain.smart_lists.smart_list_item import SmartListItem
from domain.smart_lists.smart_list_tag import SmartListTag
from domain.smart_lists.smart_list_tag_name import SmartListTagName


class SmartListNotionManager(abc.ABC):
    """A manager of Notion-side smart lists."""

    @abc.abstractmethod
    def upsert_smart_list(self, smart_list: SmartList) -> None:
        """Upsert a smart list on Notion-side."""

    @abc.abstractmethod
    def remove_smart_list(self, smart_list: SmartList) -> None:
        """Remove a smart list on Notion-side."""

    @abc.abstractmethod
    def upsert_smart_list_tag(self, smart_list_tag: SmartListTag) -> None:
        """Upsert a smart list tag on Notion-side."""

    @abc.abstractmethod
    def remove_smart_list_tag(self, smart_list_tag: SmartListTag) -> None:
        """Remove a smart list tag on Notion-side."""

    @abc.abstractmethod
    def upsert_smart_list_item(self, smart_list_item: SmartListItem, tags: Iterable[SmartListTagName]) -> None:
        """Upsert a smart list item on Notion-side."""

    @abc.abstractmethod
    def remove_smart_list_item(self, smart_list_item: SmartListItem) -> None:
        """Remove a smart list item on Notion-side."""
