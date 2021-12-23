"""The centralised point for interacting with Notion vacations."""
import logging
from typing import Final, ClassVar, Iterable

from notion.collection import CollectionRowBlock

from domain.adate import ADate
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from domain.vacations.notion_vacation import NotionVacation
from domain.vacations.vacation import Vacation
from domain.workspaces.notion_workspace import NotionWorkspace
from framework.base.entity_id import EntityId
from framework.base.timestamp import Timestamp
from framework.json import JSONDictType
from framework.notion import NotionId
from remote.notion.common import NotionPageLink, NotionLockKey
from remote.notion.infra.client import NotionClient, NotionCollectionSchemaProperties, NotionFieldProps, NotionFieldShow
from remote.notion.infra.collections_manager import CollectionsManager
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionVacationsManager(VacationNotionManager):
    """The centralised point for interacting with Notion vacations."""

    _KEY: ClassVar[str] = "vacations"
    _PAGE_NAME: ClassVar[str] = "Vacations"

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
                            "value": "True"
                        }
                    }
                }]
            }
        }
    }

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _collections_manager: Final[CollectionsManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            collections_manager: CollectionsManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._collections_manager = collections_manager

    def upsert_root_page(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root page for the vacations section."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(self._KEY),
            parent_page=NotionPageLink(notion_workspace.notion_id),
            name=self._PAGE_NAME,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "database_view_id": self._DATABASE_VIEW_SCHEMA
            })

    def upsert_vacation(self, vacation: Vacation) -> NotionVacation:
        """Create a vacation."""
        new_notion_vacation = NotionVacation.new_notion_row(vacation, None)
        return self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{vacation.ref_id}"),
            collection_key=NotionLockKey(self._KEY),
            new_row=new_notion_vacation,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def save_vacation(self, vacation: NotionVacation) -> NotionVacation:
        """Update a Notion-side vacation with new data."""
        return self._collections_manager.save_collection_item(
            key=NotionLockKey(f"{vacation.ref_id}"),
            collection_key=NotionLockKey(self._KEY),
            row=vacation,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def remove_vacation(self, ref_id: EntityId) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        self._collections_manager.remove_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(self._KEY))

    def load_all_vacations(self) -> Iterable[NotionVacation]:
        """Retrieve all the Notion-side vacation items."""
        return self._collections_manager.load_all_collection_items(
            collection_key=NotionLockKey(self._KEY),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def load_all_saved_vacation_ref_ids(self) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the vacations."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(self._KEY))

    def load_all_saved_vacation_notion_ids(self) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for the vacations."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(self._KEY))

    def drop_all_vacations(self) -> None:
        """Remove all vacations Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(self._KEY))

    def link_local_and_notion_entries(self, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(self._KEY),
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
            notion_row.ref_id = row.ref_id

        return notion_row

    def _copy_notion_row_to_row(self, vacation_notion_row: CollectionRowBlock) -> NotionVacation:
        """Transform the live system data to something suitable for basic storage."""
        return NotionVacation(
            notion_id=vacation_notion_row.id,
            name=vacation_notion_row.title,
            archived=vacation_notion_row.archived or False,
            start_date=ADate.from_notion(self._global_properties.timezone, vacation_notion_row.start_date)
            if vacation_notion_row.start_date else None,
            end_date=ADate.from_notion(self._global_properties.timezone, vacation_notion_row.end_date)
            if vacation_notion_row.end_date else None,
            last_edited_time=Timestamp.from_notion(vacation_notion_row.last_edited_time),
            ref_id=vacation_notion_row.ref_id)
