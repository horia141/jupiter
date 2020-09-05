"""The controller for smart lists."""
from typing import Final

from service.smart_lists import SmartListsService, SmartList


class SmartListsController:
    """The controller for smart lists."""

    _smart_lists_service: Final[SmartListsService]

    def __init__(self, smart_lists_service: SmartListsService) -> None:
        """Controller."""
        self._smart_lists_service = smart_lists_service

    def create_smart_list(self, name: str) -> SmartList:
        """Create a smart list."""
        return self._smart_lists_service.create_smart_list(name)
