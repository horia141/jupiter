"""The handler of ad-hoc pages on Notion side."""
import typing
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Final

from framework.json import JSONDictType
from framework.base.notion_id import NotionId
from remote.notion.common import NotionPageLink, NotionLockKey, NotionPageLinkExtra
from remote.notion.infra.connection import NotionConnection
from repository.yaml.infra.storage import BaseRecordRow, RecordsStorage
from utils.time_provider import TimeProvider


@dataclass()
class _PageLockRow(BaseRecordRow):
    """Information about a Notion-side page."""
    page_id: NotionId


class PagesManager:
    """The handler of ad-hoc pages on Notion side."""

    _STORAGE_PATH: typing.ClassVar[Path] = Path("./notion.pages.yaml")

    _connection: Final[NotionConnection]
    _storage: Final[RecordsStorage[_PageLockRow]]

    def __init__(self, time_provider: TimeProvider, connection: NotionConnection) -> None:
        """Constructor."""
        self._connection = connection
        self._storage = RecordsStorage[_PageLockRow](self._STORAGE_PATH, time_provider, self)

    def __enter__(self) -> 'PagesManager':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def upsert_page(self, key: NotionLockKey, name: str, parent_page: NotionPageLink) -> NotionPageLink:
        """Create a page with a given name."""
        found_page_lock_row = self._storage.load_optional(key)

        notion_client = self._connection.get_notion_client()

        if found_page_lock_row:
            page_block = notion_client.get_regular_page(found_page_lock_row.page_id)
            if page_block.alive:
                page_block.title = name

                if page_block.get("parent_id") != parent_page.page_id:
                    # Kind of expensive operation here!
                    page_block.move_to(notion_client.get_regular_page(parent_page.page_id))

                self._storage.update(found_page_lock_row)

                return NotionPageLink(page_id=page_block.id)

        parent_page_block = notion_client.get_regular_page(parent_page.page_id)
        new_page_block = notion_client.create_regular_page(name, parent_page_block)

        self._storage.create(_PageLockRow(key=key, page_id=new_page_block.id))

        return NotionPageLink(page_id=new_page_block.id)

    def remove_page(self, key: NotionLockKey) -> NotionPageLink:
        """Remove a page with a given key."""
        found_page_lock_row = self._storage.load(key)
        notion_client = self._connection.get_notion_client()

        page_block = notion_client.get_regular_page(found_page_lock_row.page_id)
        page_block.remove()

        return NotionPageLink(page_id=found_page_lock_row.page_id)

    def get_page(self, key: NotionLockKey) -> NotionPageLink:
        """Get a page with a given key."""
        found_page_lock_row = self._storage.load(key)
        return NotionPageLink(page_id=found_page_lock_row.page_id)

    def get_page_extra(self, key: NotionLockKey) -> NotionPageLinkExtra:
        """Get a page with a given key."""
        found_page_lock_row = self._storage.load(key)
        notion_client = self._connection.get_notion_client()

        page_block = notion_client.get_regular_page(found_page_lock_row.page_id)
        return NotionPageLinkExtra(page_id=found_page_lock_row.page_id, name=page_block.title)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "page_id": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _PageLockRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _PageLockRow(
            key=NotionLockKey(typing.cast(str, storage_form["key"])),
            page_id=NotionId.from_raw(typing.cast(str, storage_form["page_id"])))

    @staticmethod
    def live_to_storage(live_form: _PageLockRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "page_id": str(live_form.page_id)
        }
