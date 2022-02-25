"""The centralised point for interacting with Notion smart lists."""
import typing
from typing import ClassVar, Final, List

from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListNotFoundError, NotionSmartListTagNotFoundError, NotionSmartListItemNotFoundError
from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_collection import NotionSmartListCollection
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import NotionCollectionSchemaProperties, NotionFieldProps, NotionFieldShow
from jupiter.remote.notion.infra.collections_manager import NotionCollectionsManager, NotionCollectionNotFoundError, \
    NotionCollectionFieldTagNotFoundError, NotionCollectionItemNotFoundError
from jupiter.remote.notion.infra.pages_manager import NotionPagesManager
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider


class NotionSmartListsManager(SmartListNotionManager):
    """The centralised point for interacting with Notion smart lists."""

    _KEY: ClassVar[str] = "smart-lists"
    _PAGE_NAME: ClassVar[str] = "Smart Lists"
    _PAGE_ICON: ClassVar[str] = "🏛️"

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
                            "value": True
                        }
                    }
                }, {
                    "property": "is-done",
                    "filter": {
                        "operator": "checkbox_is",
                        "value": {
                            "type": "exact",
                            "value": True
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
                            "value": True
                        }
                    }
                }, {
                    "property": "is-done",
                    "filter": {
                        "operator": "checkbox_is_not",
                        "value": {
                            "type": "exact",
                            "value": True
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

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _pages_manager: Final[NotionPagesManager]
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider, pages_manager: NotionPagesManager,
            collections_manager: NotionCollectionsManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._pages_manager = pages_manager
        self._collections_manager = collections_manager

    def upsert_root_page(
            self, notion_workspace: NotionWorkspace, smart_list_collection: NotionSmartListCollection) -> None:
        """Upsert the root page for the smart lists section."""
        self._pages_manager.upsert_page(
            key=NotionLockKey(f"{self._KEY}:{smart_list_collection.ref_id}"),
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            parent_page_notion_id=notion_workspace.notion_id)

    def upsert_smart_list(self, smart_list_collection_ref_id: EntityId, smart_list: NotionSmartList) -> NotionSmartList:
        """Upsert a smart list on Notion-side."""
        root_page = self._pages_manager.get_page(NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}"))
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list.ref_id}"),
            parent_page_notion_id=root_page.notion_id,
            name=smart_list.name,
            icon=smart_list.icon,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                ("database_view_id", self._DATABASE_VIEW_SCHEMA),
                ("database_done_view_id", self._DATABASE_VIEW_DONE_SCHEMA),
                ("database_not_done_view_id", self._DATABASE_VIEW_NOT_DONE_SCHEMA)
            ])
        return smart_list

    def save_smart_list(self, smart_list_collection_ref_id: EntityId, smart_list: NotionSmartList) -> NotionSmartList:
        """Save a smart list collection."""
        try:
            self._collections_manager.save_collection(
                key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list.ref_id}"),
                new_name=smart_list.name,
                new_icon=smart_list.icon,
                new_schema=self._SCHEMA)
            return smart_list
        except NotionCollectionNotFoundError as err:
            raise NotionSmartListNotFoundError(f"Smart list with id {smart_list.ref_id} was not found") from err

    def load_smart_list(self, smart_list_collection_ref_id: EntityId, ref_id: EntityId) -> NotionSmartList:
        """Load a smart list collection."""
        try:
            smart_list_link = self._collections_manager.load_collection(
                key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionSmartListNotFoundError(f"Smart list with id {ref_id} was not found") from err

        return NotionSmartList(
            name=smart_list_link.name,
            icon=smart_list_link.icon,
            ref_id=ref_id,
            notion_id=smart_list_link.collection_notion_id)

    def remove_smart_list(self, smart_list_collection_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a smart list on Notion-side."""
        try:
            self._collections_manager.remove_collection(
                NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionSmartListNotFoundError(f"Smart list with id {ref_id} was not found") from err

    def upsert_smart_list_tag(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            smart_list_tag: NotionSmartListTag) -> NotionSmartListTag:
        """Upsert a smart list tag on Notion-side."""
        self._collections_manager.upsert_collection_field_tag(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
            field="tags",
            key=NotionLockKey(f"{smart_list_tag.ref_id}"),
            ref_id=typing.cast(EntityId, smart_list_tag.ref_id),
            tag=smart_list_tag.name)
        return smart_list_tag

    def save_smart_list_tag(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            smart_list_tag: NotionSmartListTag) -> NotionSmartListTag:
        """Update the Notion-side smart list tag with new data."""
        try:
            self._collections_manager.save_collection_field_tag(
                collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                key=NotionLockKey(f"{smart_list_tag.ref_id}"), field="tags", tag=smart_list_tag.name)
            return smart_list_tag
        except NotionCollectionFieldTagNotFoundError as err:
            raise NotionSmartListTagNotFoundError(
                f"Smart list tag with id {smart_list_tag.ref_id} was not found") from err

    def load_smart_list_tag(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            ref_id: EntityId) -> NotionSmartListTag:
        """Retrieve a the Notion-side smart list tag."""
        try:
            notion_link = self._collections_manager.load_collection_field_tag(
                collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                field="tags",
                key=NotionLockKey(f"{ref_id}"),
                ref_id=ref_id)
            return NotionSmartListTag(
                name=notion_link.name, notion_id=notion_link.notion_id, ref_id=ref_id,
                archived=False, last_edited_time=self._time_provider.get_current_time())
        except NotionCollectionFieldTagNotFoundError as err:
            raise NotionSmartListTagNotFoundError(
                f"Smart list tag with id {ref_id} was not found") from err

    def load_all_smart_list_tags(
            self, smart_list_collection_ref_id: EntityId,
            smart_list_ref_id: EntityId) -> typing.Iterable[NotionSmartListTag]:
        """Retrieve all the Notion-side smart list tags."""
        return [NotionSmartListTag(name=s.name,
                                   notion_id=s.notion_id,
                                   ref_id=s.ref_id if s.ref_id != BAD_REF_ID else None,
                                   archived=False,
                                   last_edited_time=self._time_provider.get_current_time())
                for s in self._collections_manager.load_all_collection_field_tags(
                    collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                    field="tags")]

    def remove_smart_list_tag(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            ref_id: typing.Optional[EntityId]) -> None:
        """Remove a smart list tag on Notion-side."""
        try:
            self._collections_manager.remove_collection_field_tag(
                collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                key=NotionLockKey(f"{ref_id}"))
        except NotionCollectionFieldTagNotFoundError as err:
            raise NotionSmartListTagNotFoundError(
                f"Smart list tag with id {ref_id} was not found") from err

    def drop_all_smart_list_tags(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId) -> None:
        """Remove all smart list tags Notion-side."""
        self._collections_manager.drop_all_collection_field_tags(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
            field="tags")

    def link_local_and_notion_tag_for_smart_list(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId, ref_id: EntityId,
            notion_id: NotionId) -> None:
        """Link a local tag with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_collection_field_tag(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            field="tags",
            ref_id=ref_id,
            notion_id=notion_id)

    def load_all_saved_smart_list_tags_notion_ids(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId) -> typing.Iterable[NotionId]:
        """Retrieve all the Notion ids for the smart list tags."""
        return self._collections_manager.load_all_saved_collection_field_tag_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
            field="tags")

    def upsert_smart_list_item(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            smart_list_item: NotionSmartListItem) -> NotionSmartListItem:
        """Upsert a smart list item on Notion-side."""
        link = \
            self._collections_manager.upsert_collection_item(
                key=NotionLockKey(f"{smart_list_item.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                new_row=smart_list_item,
                copy_row_to_notion_row=self._copy_row_to_notion_row)
        return link.item_info

    def save_smart_list_item(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            smart_list_item: NotionSmartListItem) -> NotionSmartListItem:
        """Update the Notion-side smart list with new data."""
        try:
            link = \
                self._collections_manager.save_collection_item(
                    key=NotionLockKey(f"{smart_list_item.ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                    row=smart_list_item,
                    copy_row_to_notion_row=self._copy_row_to_notion_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionSmartListItemNotFoundError(
                f"Smart list item with id {smart_list_item.ref_id} could not be found") from err

    def load_smart_list_item(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId,
            ref_id: EntityId) -> NotionSmartListItem:
        """Retrieve a particular smart list item."""
        try:
            link = \
                self._collections_manager.load_collection_item(
                    key=NotionLockKey(f"{ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionSmartListItemNotFoundError(
                f"Smart list item with id {ref_id} could not be found") from err

    def load_all_smart_list_items(
            self, smart_list_collection_ref_id: EntityId,
            smart_list_ref_id: EntityId) -> typing.Iterable[NotionSmartListItem]:
        """Retrieve all the Notion-side smart list items."""
        return [l.item_info for l in
                self._collections_manager.load_all_collection_items(
                    collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)]

    def remove_smart_list_item(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a smart list item on Notion-side."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"))
        except NotionCollectionItemNotFoundError as err:
            raise NotionSmartListItemNotFoundError(
                f"Smart list item with id {ref_id} could not be found") from err

    def drop_all_smart_list_items(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId) -> None:
        """Remove all smart list items Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"))

    def link_local_and_notion_entries_for_smart_list(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId, ref_id: EntityId,
            notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def load_all_saved_smart_list_items_notion_ids(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId) -> typing.Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these smart lists items."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"))

    def load_all_saved_smart_list_items_ref_ids(
            self, smart_list_collection_ref_id: EntityId, smart_list_ref_id: EntityId) -> typing.Iterable[EntityId]:
        """Retrieve all the saved ref ids for the smart list items."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{smart_list_collection_ref_id}:{smart_list_ref_id}"))

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionSmartListItem, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.is_done = row.is_done
            notion_row.tags = row.tags
            notion_row.url = row.url
            notion_row.archived = row.archived
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = str(row.ref_id) if row.ref_id else None

        return notion_row

    def _copy_notion_row_to_row(self, notion_row: CollectionRowBlock) -> NotionSmartListItem:
        """Copy the fields of the local row to the actual Notion structure."""
        # pylint: disable=no-self-use
        tags: List[str] = []
        if len(notion_row.tags) == 0:
            tags = []
        elif len(notion_row.tags) == 1 and notion_row.tags[0] == "":
            tags = []
        else:
            tags = notion_row.tags
        return NotionSmartListItem(
            name=notion_row.title,
            is_done=notion_row.is_done,
            tags=tags,
            url=notion_row.url,
            archived=notion_row.archived,
            last_edited_time=Timestamp.from_notion(notion_row.last_edited_time),
            ref_id=EntityId.from_raw(notion_row.ref_id) if notion_row.ref_id else None,
            notion_id=NotionId.from_raw(notion_row.id))
