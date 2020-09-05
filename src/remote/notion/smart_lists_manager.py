"""The centralised point for interacting with Notion smart lists."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, ClassVar, Final

from models.basic import Timestamp, EntityId
from remote.notion.infra.collection import BasicRowType
from remote.notion.common import NotionPageLink, NotionLockKey
from remote.notion.infra.collections_manager import CollectionsManager
from remote.notion.infra.pages_manager import PagesManager


@dataclass()
class SmartListItemRow(BasicRowType):
    """A smart list item on Notion side."""

    name: str
    archived: bool
    last_edited_time: Timestamp


class NotionSmartListsManager:
    """The centralised point for interacting with Notion smart lists."""

    _KEY: ClassVar[str] = "smart-lists"
    _PAGE_NAME: ClassVar[str] = "Smart Lists"
    _LOCK_FILE_PATH: ClassVar[Path] = Path("/data/smart-lists.lock.yaml")

    _pages_manager: Final[PagesManager]
    _collections_manager: Final[CollectionsManager]

    def __init__(self, pages_manager: PagesManager, collections_manager: CollectionsManager) -> None:
        """Constructor."""
        self._pages_manager = pages_manager
        self._collections_manager = collections_manager

    def upsert_root_page(self, parent_page_link: NotionPageLink) -> None:
        """Upsert the root page for the smart lists section."""
        self._pages_manager.upsert_page(NotionLockKey(self._KEY), self._PAGE_NAME, parent_page_link)

    def upsert_smart_list(self, ref_id: EntityId, name: str) -> None:
        """Upsert the Notion-side smart list."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        self._collections_manager.upsert_collection(f"{self._KEY}:{ref_id}", name, root_page)

    def upsert_smart_list_item(
            self, smart_list_ref_id: EntityId, ref_id: EntityId, name: str, url: Optional[str]) -> None:
        """Upsert the Notion-side smart list item."""
        collection = self._collections_manager.get_collection(f"{self._KEY}:{smart_list_ref_id}")
        self._collections_manager.upsert_collection_item(
            collection, f"{self._KEY}:{smart_list_ref_id}:{ref_id}", name, url)
