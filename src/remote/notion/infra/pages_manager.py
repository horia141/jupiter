"""The handler of ad-hoc pages on Notion side."""
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Final

import typing

from remote.notion.common import NotionPageLink, NotionId, NotionLockKey, PageNotFoundError
from remote.notion.infra.connection import NotionConnection
from utils.storage import StructuredCollectionStorage, JSONDictType


@dataclass()
class _PageLockRow:
    """Information about a Notion-side page."""
    key: NotionLockKey
    page_id: NotionId


class PagesManager:
    """The handler of ad-hoc pages on Notion side."""

    _STORAGE_PATH: typing.ClassVar[Path] = Path("/data/notion.pages.yaml")

    _connection: Final[NotionConnection]
    _structured_storage: Final[StructuredCollectionStorage[_PageLockRow]]

    def __init__(self, connection: NotionConnection) -> None:
        """Constructor."""
        self._connection = connection
        self._structured_storage = StructuredCollectionStorage(self._STORAGE_PATH, self)

    def __enter__(self) -> 'PagesManager':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def upsert_page(self, key: NotionLockKey, name: str, parent_page: Optional[NotionPageLink]) -> NotionPageLink:
        """Create a page with a given name."""
        page_lock_rows_next_idx, page_lock_rows = self._structured_storage.load()

        found_page_lock_row = self._find_lock_by_key(key, page_lock_rows)

        notion_client = self._connection.get_notion_client()

        if found_page_lock_row:
            page_block = notion_client.get_regular_page(found_page_lock_row.page_id)
            page_block.title = name

            return NotionPageLink(page_id=page_block.id)
        else:
            if parent_page:
                parent_page_block = notion_client.get_regular_page(parent_page.page_id)
                new_page_block = notion_client.create_regular_page(name, parent_page_block)
            else:
                new_page_block = notion_client.create_regular_page(name)

            page_lock_rows.append(_PageLockRow(key=key, page_id=new_page_block.id))
            self._structured_storage.save((page_lock_rows_next_idx + 1, page_lock_rows))

            return NotionPageLink(page_id=new_page_block.id)

    def get_page(self, key: NotionLockKey) -> NotionPageLink:
        """Get a page with a given key."""
        _, page_lock_rows = self._structured_storage.load()

        found_page_lock_row = self._find_lock_by_key(key, page_lock_rows)

        if not found_page_lock_row:
            raise PageNotFoundError(f"Could not find page for key '{key}'")

        return NotionPageLink(page_id=found_page_lock_row.page_id)

    @staticmethod
    def _find_lock_by_key(key: NotionLockKey, page_lock_rows: typing.List[_PageLockRow]) -> Optional[_PageLockRow]:
        try:
            return next(plr for plr in page_lock_rows if plr.key == key)
        except StopIteration:
            return None

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "page_id": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _PageLockRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _PageLockRow(
            key=NotionLockKey(typing.cast(str, storage_form["key"])),
            page_id=NotionId(typing.cast(str, storage_form["page_id"])))

    @staticmethod
    def live_to_storage(live_form: _PageLockRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "key": live_form.key,
            "page_id": live_form.page_id
        }
