"""The centralised point for interacting with Notion vacations."""
import logging
from typing import Final, ClassVar, Iterable, Optional

from notion.collection import CollectionRowBlock

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.domain.vacations.notion_vacation import NotionVacation
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import NotionClient, NotionCollectionSchemaProperties, NotionFieldProps, \
    NotionFieldShow
from jupiter.remote.notion.infra.collections_manager import NotionCollectionsManager, NotionCollectionItemNotFoundError
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionVacationsManager(VacationNotionManager):
    """The centralised point for interacting with Notion vacations."""

    _KEY: ClassVar[str] = "vacations"
    _PAGE_NAME: ClassVar[str] = "Vacations"
    _PAGE_ICON: ClassVar[str] = "🌴"

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "start-date": {
            "name": "Start Date",
            "type": "date"
        },
        "end-date": {
            "name": "End Date",
            "type": "date"
        },
        "last-edited-time": {
            "name": "Last Edited Time",
            "type": "last_edited_time"
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        }
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("start-date", NotionFieldShow.SHOW),
        NotionFieldProps("end-date", NotionFieldShow.SHOW),
        NotionFieldProps("archived", NotionFieldShow.SHOW),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

    _DATABASE_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Database",
        "type": "table",
        "format": {
            "table_properties": [{
                "width": 300,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True,
            }, {
                "width": 200,
                "property": "start-date",
                "visible": True
            }, {
                "width": 200,
                "property": "end-date",
                "visible": True
            }, {
                "width": 200,
                "property": "last-edited-time",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": False
            }]
        },
        "query2": {
            "sort": [{
                "property": "start-date",
                "direction": "ascending"
            }, {
                "property": "end-date",
                "direction": "ascending"
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
                }]
            }
        }
    }

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            collections_manager: NotionCollectionsManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._collections_manager = collections_manager

    def upsert_trunk(
            self, parent: NotionWorkspace, trunk: NotionVacationCollection) -> None:
        """Upsert the root page for the vacations section."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{trunk.ref_id}"),
            parent_page_notion_id=parent.notion_id,
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                ("database_view_id", self._DATABASE_VIEW_SCHEMA)
            ])

    def upsert_leaf(self, trunk_ref_id: EntityId, leaf: NotionVacation, extra_info: None) -> NotionVacation:
        """Create a vacation."""
        link = \
            self._collections_manager.upsert_collection_item(
                key=NotionLockKey(f"{leaf.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                new_row=leaf,
                copy_row_to_notion_row=self._copy_row_to_notion_row)
        return link.item_info

    def save_leaf(
            self, trunk_ref_id: EntityId, leaf: NotionVacation, extra_info: Optional[None] = None) -> NotionVacation:
        """Update a Notion-side vacation with new data."""
        try:
            link = \
                self._collections_manager.save_collection_item(
                    key=NotionLockKey(f"{leaf.ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                    row=leaf,
                    copy_row_to_notion_row=self._copy_row_to_notion_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionVacationNotFoundError(f"Vacation with id {leaf.ref_id} could not be found") from err

    def load_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> NotionVacation:
        """Load a Notion-side vacation."""
        try:
            link = \
                self._collections_manager.load_collection_item(
                    key=NotionLockKey(f"{leaf_ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionVacationNotFoundError(f"Vacation with id {leaf_ref_id} could not be found") from err

    def load_all_leaves(self, trunk_ref_id: EntityId) -> Iterable[NotionVacation]:
        """Retrieve all the Notion-side vacation items."""
        return [l.item_info for l in
                self._collections_manager.load_all_collection_items(
                    collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)]

    def remove_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))
        except NotionCollectionItemNotFoundError as err:
            raise NotionVacationNotFoundError(f"Vacation with id {leaf_ref_id} could not be found") from err

    def drop_all_leaves(self, trunk_ref_id: EntityId) -> None:
        """Remove all vacations Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))

    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the vacations."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))

    def load_all_saved_notion_ids(self, trunk_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for the vacations."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))

    def link_local_and_notion_leaves(
            self, trunk_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionVacation, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.archived = row.archived
            notion_row.start_date = \
                row.start_date.to_notion(self._global_properties.timezone) if row.start_date else None
            notion_row.end_date = row.end_date.to_notion(self._global_properties.timezone) if row.end_date else None
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = str(row.ref_id) if row.ref_id else None

        return notion_row

    def _copy_notion_row_to_row(self, vacation_notion_row: CollectionRowBlock) -> NotionVacation:
        """Transform the live system data to something suitable for basic storage."""
        return NotionVacation(
            notion_id=NotionId.from_raw(vacation_notion_row.id),
            name=vacation_notion_row.title,
            archived=vacation_notion_row.archived or False,
            start_date=ADate.from_notion(self._global_properties.timezone, vacation_notion_row.start_date)
            if vacation_notion_row.start_date else None,
            end_date=ADate.from_notion(self._global_properties.timezone, vacation_notion_row.end_date)
            if vacation_notion_row.end_date else None,
            last_edited_time=Timestamp.from_notion(vacation_notion_row.last_edited_time),
            ref_id=EntityId.from_raw(vacation_notion_row.ref_id) if vacation_notion_row.ref_id else None)
