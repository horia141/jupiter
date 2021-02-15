"""The centralised point for interacting with Notion smart lists."""
from dataclasses import dataclass
from typing import Optional, ClassVar, Final, List
import typing

from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from models.basic import Timestamp, EntityId, BasicValidator, Tag
from remote.notion.common import NotionPageLink, NotionLockKey, NotionId
from remote.notion.infra.client import NotionCollectionSchemaProperties, NotionFieldProps, NotionFieldShow
from remote.notion.infra.collections_manager import CollectionsManager, BaseItem
from remote.notion.infra.pages_manager import PagesManager
from utils.storage import JSONDictType
from utils.time_provider import TimeProvider


@dataclass()
class SmartListNotionCollection(BaseItem):
    """A smart list collection on Notion side."""

    name: str


@dataclass()
class SmartListNotionTag(BaseItem):
    """A smart list tag on Notion side."""

    name: str


@dataclass()
class SmartListNotionRow(BaseItem):
    """A smart list item on Notion side."""

    name: str
    is_done: bool
    tags: List[str]
    url: Optional[str]
    archived: bool
    last_edited_time: Timestamp


class NotionSmartListsManager:
    """The centralised point for interacting with Notion smart lists."""

    _KEY: ClassVar[str] = "smart-lists"
    _PAGE_NAME: ClassVar[str] = "Smart Lists"

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        },
        "is-done": {
            "name": "Is Done",
            "type": "checkbox"
        },
        "tags": {
            "name": "Tags",
            "type": "multi_select",
            "options": []
        },
        "url": {
            "name": "URL",
            "type": "text"
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "last-edited-time": {
            "name": "Last Edited Time",
            "type": "last_edited_time"
        },
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("is-done", NotionFieldShow.SHOW),
        NotionFieldProps("tags", NotionFieldShow.SHOW),
        NotionFieldProps("url", NotionFieldShow.SHOW),
        NotionFieldProps("archived", NotionFieldShow.SHOW),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

    _DATABASE_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "All",
        "type": "table",
        "format": {
            "table_properties": [{
                "width": 300,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "is-done",
                "visible": True
            }, {
                "width": 100,
                "property": "tags",
                "visible": True
            }, {
                "width": 100,
                "property": "url",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": True
            }]
        }
    }

    _DATABASE_VIEW_DONE_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Done",
        "type": "table",
        "query2": {
            "filter_operator": "and",
            "aggregations": [{
                "aggregator": "count"
            }],
            "filter": {
                "operator": "and",
                "filters": [{
                    "property": "archived",
                    "filter": {
                        "operator": "checkbox_is_not",
                        "value": {
                            "type": "exact",
                            "value": "True"
                        }
                    }
                }, {
                    "property": "is-done",
                    "filter": {
                        "operator": "checkbox_is",
                        "value": {
                            "type": "exact",
                            "value": "True"
                        }
                    }
                }]
            }
        },
        "format": {
            "table_properties": [{
                "width": 300,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "is-done",
                "visible": True
            }, {
                "width": 100,
                "property": "tags",
                "visible": True
            }, {
                "width": 100,
                "property": "url",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": True
            }]
        }
    }

    _DATABASE_VIEW_NOT_DONE_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Not Done",
        "type": "table",
        "query2": {
            "filter_operator": "and",
            "aggregations": [{
                "aggregator": "count"
            }],
            "filter": {
                "operator": "and",
                "filters": [{
                    "property": "archived",
                    "filter": {
                        "operator": "checkbox_is_not",
                        "value": {
                            "type": "exact",
                            "value": "True"
                        }
                    }
                }, {
                    "property": "is-done",
                    "filter": {
                        "operator": "checkbox_is_not",
                        "value": {
                            "type": "exact",
                            "value": "True"
                        }
                    }
                }]
            }
        },
        "format": {
            "table_properties": [{
                "width": 300,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "is-done",
                "visible": True
            }, {
                "width": 100,
                "property": "tags",
                "visible": True
            }, {
                "width": 100,
                "property": "url",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": True
            }]
        }
    }

    _time_provider: Final[TimeProvider]
    _basic_validator: Final[BasicValidator]
    _pages_manager: Final[PagesManager]
    _collections_manager: Final[CollectionsManager]

    def __init__(
            self, time_provider: TimeProvider, basic_validator: BasicValidator, pages_manager: PagesManager,
            collections_manager: CollectionsManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._basic_validator = basic_validator
        self._pages_manager = pages_manager
        self._collections_manager = collections_manager

    def upsert_root_page(self, parent_page_link: NotionPageLink) -> None:
        """Upsert the root page for the smart lists section."""
        self._pages_manager.upsert_page(NotionLockKey(self._KEY), self._PAGE_NAME, parent_page_link)

    def upsert_smart_list_collection(self, ref_id: EntityId, name: str) -> SmartListNotionCollection:
        """Upsert the Notion-side smart list."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        collection_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{ref_id}"),
            parent_page=root_page,
            name=name,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "database_view_id": self._DATABASE_VIEW_SCHEMA,
                "database_done_view_id": self._DATABASE_VIEW_DONE_SCHEMA,
                "database_not_done_view_id": self._DATABASE_VIEW_NOT_DONE_SCHEMA
            })

        return SmartListNotionCollection(
            name=name,
            ref_id=ref_id,
            notion_id=collection_link.collection_id)

    def load_smart_list_collection(self, smart_list_ref_id: EntityId) -> SmartListNotionCollection:
        """Load a smart list collection."""
        smart_list_link = self._collections_manager.get_collection(
            key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"))

        return SmartListNotionCollection(
            name=smart_list_link.name,
            ref_id=smart_list_ref_id,
            notion_id=smart_list_link.collection_id)

    def save_smart_list_collection(self, smart_list: SmartListNotionCollection) -> None:
        """Save a smart list collection."""
        self._collections_manager.update_collection(
            key=NotionLockKey(f"{self._KEY}:{smart_list.ref_id}"),
            new_name=smart_list.name,
            new_schema=self._SCHEMA)

    def hard_remove_smart_list_collection(self, ref_id: EntityId) -> None:
        """Hard remove a smart list item."""
        self._collections_manager.remove_collection(NotionLockKey(f"{self._KEY}:{ref_id}"))

    def upsert_smart_list_tag(self, smart_list_ref_id: EntityId, ref_id: EntityId, name: Tag) -> SmartListNotionTag:
        """Upsert a smart list tag."""
        smart_list_tag_link = self._collections_manager.upsert_collection_field_tag(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            field="tags",
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            tag=name)
        return SmartListNotionTag(notion_id=smart_list_tag_link.notion_id, ref_id=ref_id, name=name)

    def load_all_smart_list_tags(self, smart_list_ref_id: EntityId) -> typing.Iterable[SmartListNotionTag]:
        """Retrieve all the Notion-side smart list tags."""
        return [SmartListNotionTag(name=s.name, notion_id=s.notion_id, ref_id=s.ref_id)
                for s in self._collections_manager.load_all_collection_field_tags(
                    collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
                    field="tags")]

    def save_smart_list_tag(
            self, smart_list_ref_id: EntityId, ref_id: EntityId,
            new_smart_list_item_tag: SmartListNotionTag) -> SmartListNotionTag:
        """Update the Notion-side smart list tag with new data."""
        smart_list_tag_link = self._collections_manager.save_collection_field_tag(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            field="tags",
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            tag=new_smart_list_item_tag.name)
        return SmartListNotionTag(
            notion_id=smart_list_tag_link.notion_id, ref_id=ref_id, name=new_smart_list_item_tag.name)

    def load_all_saved_smart_list_tags_notion_ids(self, smart_list_ref_id: EntityId) -> typing.Iterable[NotionId]:
        """Retrieve all the Notion ids for the smart list tags."""
        return self._collections_manager.load_all_saved_collection_field_tag_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            field="tags")

    def drop_all_smart_list_tags(self, smart_list_ref_id: EntityId) -> None:
        """Remove all smart list tags Notion-side."""
        self._collections_manager.drop_all_collection_field_tags(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            field="tags")

    def link_local_and_notion_tag_for_smart_list(
            self, smart_list_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local tag with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_collection_field_tags(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            field="tags",
            ref_id=ref_id,
            notion_id=notion_id)

    def hard_remove_smart_list_tag(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> None:
        """Hard remove a smart list tag."""
        self._collections_manager.hard_remove_collection_field_tag(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            key=NotionLockKey(f"{ref_id}"))

    def upsert_smart_list_item(
            self, smart_list_ref_id: EntityId, ref_id: EntityId, name: str, is_done: bool, tags: List[str],
            url: Optional[str], archived: bool) -> SmartListNotionRow:
        """Upsert the Notion-side smart list item."""
        new_row = SmartListNotionRow(
            name=name,
            url=url,
            is_done=is_done,
            tags=tags,
            archived=archived,
            last_edited_time=self._time_provider.get_current_time(),
            ref_id=ref_id,
            notion_id=typing.cast(NotionId, None))
        self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            new_row=new_row,
            copy_row_to_notion_row=self._copy_row_to_notion_row)
        return new_row

    def load_all_smart_list_items(self, smart_list_ref_id: EntityId) -> typing.Iterable[SmartListNotionRow]:
        """Retrieve all the Notion-side smart list items."""
        return self._collections_manager.load_all(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def load_smart_list_item(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> SmartListNotionRow:
        """Retrieve the Notion-side smart list item associated with a particular entity."""
        return self._collections_manager.load(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def save_smart_list_item(
            self, smart_list_ref_id: EntityId, ref_id: EntityId,
            new_smart_list_item_row: SmartListNotionRow) -> SmartListNotionRow:
        """Update the Notion-side smart list with new data."""
        return self._collections_manager.save(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            row=new_smart_list_item_row,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def archive_smart_list_item(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a particular smart list item."""
        self._collections_manager.quick_archive(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"))

    def hard_remove_smart_list_item(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> None:
        """Hard remove a particular smart list item."""
        self._collections_manager.hard_remove(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"))

    def load_all_saved_smart_list_items_notion_ids(self, smart_list_ref_id: EntityId) -> typing.Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these smart lists items."""
        return self._collections_manager.load_all_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"))

    def load_all_saved_smart_list_items_ref_ids(self, smart_list_ref_id: EntityId) -> typing.Iterable[EntityId]:
        """Retrieve all the saved ref ids for the smart list items."""
        return self._collections_manager.load_all_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"))

    def drop_all_smart_list_items(self, smart_list_ref_id: EntityId) -> None:
        """Remove all smart list items Notion-side."""
        self._collections_manager.drop_all(collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"))

    def link_local_and_notion_entries_for_smart_list(
            self, smart_list_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: SmartListNotionRow, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.is_done = row.is_done
            notion_row.tags = row.tags
            notion_row.url = row.url
            notion_row.archived = row.archived
            notion_row.last_edited_time = self._basic_validator.timestamp_to_notion_timestamp(row.last_edited_time)
            notion_row.ref_id = row.ref_id

        return notion_row

    def _copy_notion_row_to_row(self, notion_row: CollectionRowBlock) -> SmartListNotionRow:
        """Copy the fields of the local row to the actual Notion structure."""
        tags: List[str] = []
        if len(notion_row.tags) == 0:
            tags = []
        elif len(notion_row.tags) == 1 and notion_row.tags[0] == "":
            tags = []
        else:
            tags = notion_row.tags
        return SmartListNotionRow(
            name=notion_row.title,
            is_done=notion_row.is_done,
            tags=tags,
            url=notion_row.url,
            archived=notion_row.archived,
            last_edited_time=self._basic_validator.timestamp_from_notion_timestamp(notion_row.last_edited_time),
            ref_id=notion_row.ref_id,
            notion_id=notion_row.id)
