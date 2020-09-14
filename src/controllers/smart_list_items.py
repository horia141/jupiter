"""The controller for smart list items."""
from typing import Final, Optional

from models.basic import EntityId
from service.smart_lists import SmartListsService, SmartListItem


class SmartListItemsController:
    """The controller for smart list items."""

    _smart_lists_service: Final[SmartListsService]

    def __init__(self, smart_lists_service: SmartListsService) -> None:
        """Controller."""
        self._smart_lists_service = smart_lists_service

    def create_smart_list_item(self, smart_list_ref_id: EntityId, name: str, url: Optional[str]) -> SmartListItem:
        """Create a smart list item."""
        return self._smart_lists_service.create_smart_list_item(smart_list_ref_id, name, url)
