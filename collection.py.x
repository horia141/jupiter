"""Abstract base class for collections of Notion rows, with a page and several views for them."""
import abc
from pathlib import Path
from typing import TypeVar, Generic, Iterable

from notion.block import PageBlock

from models.basic import EntityId
from utils.structured_storage import StructuredStorage

CollectionRowType = TypeVar("CollectionRowType")
CollectionLockType = TypeVar("CollectionLockType")


class Collection(abc.ABC, Generic[CollectionRowType, CollectionLockType]):
    """An abstract base class for collections of Notion rows, with a page and several views for them."""

    _lock_file_path: Path
    _structured_storage: StructuredStorage[CollectionLockType]

    def __init__(self) -> None:
        """Constructor."""
        pass

    def upsert_notion_structure(self, parent_page: PageBlock) -> None:
        pass

    def create(self) -> CollectionRowType:
        pass

    def link_local_and_notion_entities(self) -> None:
        pass

    def remove_by_id(self) -> None:
        pass

    def load_all(self) -> Iterable[CollectionRowType]:
        pass

    def load_by_id(self, ref_id: EntityId) -> CollectionRowType:
        pass

    def save(self, new_row: CollectionLockType) -> None:
        pass

    def hard_remove_by_id(self, ref_id: EntityId) -> None:
        pass
