"""The controller for smart list items."""
from typing import Final, Optional

from service.smart_lists import SmartListsService, SmartListItem


class SmartListItemsController:
    """The controller for smart list items."""

    _smart_lists_service: Final[SmartListsService]

    def __init__(self, smart_lists_service: SmartListsService) -> None:
        """Controller."""
        self._smart_lists_service = smart_lists_service

    def create_smart_list_item(self, name: str, url: Optional[str]) -> SmartListItem:
        """Create a smart list."""
        return self._smart_lists_service.create_smart_list_item(name, url)
