"""The collection for vacations."""
import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
import typing
from typing import Final, Optional, Dict, ClassVar, Iterable, cast, Type

import pendulum
from notion.collection import CollectionRowBlock

from models.basic import EntityId
from remote.notion.client import NotionClient
from remote.notion.collection import BasicRowType, NotionCollection, NotionCollectionKWArgsType
from remote.notion.common import NotionId, NotionPageLink, NotionCollectionLink
from remote.notion.connection import NotionConnection
from utils.storage import JSONDictType

LOGGER = logging.getLogger(__name__)


@dataclass()
class VacationRow(BasicRowType):
    """A vacation row on Notion side."""

    notion_id: NotionId
    name: str
    archived: bool
    start_date: Optional[pendulum.DateTime]
    end_date: Optional[pendulum.DateTime]
    ref_id: Optional[str]


class VacationsCollection:
    """A collection on Notion side for vacations."""

    _LOCK_FILE_PATH: ClassVar[Path] = Path("/data/vacations.lock.yaml")
    _DISCRIMINANT: ClassVar[str] = "vacations"

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
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        }
    }
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
                "visible": False,
            }, {
                "width": 200,
                "property": "start-date",
                "visible": True
            }, {
                "width": 200,
                "property": "end-date",
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

    _collection: Final[NotionCollection[VacationRow]]

    def __init__(self, connection: NotionConnection) -> None:
        """Constructor."""
        self._collection = NotionCollection[VacationRow](connection, self._LOCK_FILE_PATH, self)

    def __enter__(self) -> 'VacationsCollection':
        """Enter context."""
        self._collection.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._collection.exit_save()

    def upsert_vacations_structure(self, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Create/update the Notion-side structure for this collection."""
        return self._collection.upsert_structure(self._DISCRIMINANT, parent_page)

    def create_vacation(
            self, name: str, start_date: pendulum.DateTime, end_date: pendulum.DateTime,
            ref_id: EntityId) -> VacationRow:
        """Create a vacation."""
        new_vacation_row = VacationRow(
            notion_id=NotionId("FAKE-FAKE-FAKE"),
            name=name,
            archived=False,
            start_date=start_date,
            end_date=end_date,
            ref_id=ref_id)
        return cast(VacationRow, self._collection.create(self._DISCRIMINANT, new_vacation_row))

    def link_local_and_notion_entries(self, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the notion one, useful in syncing processes."""
        self._collection.link_local_and_notion_entries(self._DISCRIMINANT, ref_id, notion_id)

    def remove_vacation_by_id(self, ref_id: EntityId) -> None:
        """Remove a particular vacation."""
        self._collection.remove_by_id(self._DISCRIMINANT, ref_id)

    def load_all_vacations(self) -> Iterable[VacationRow]:
        """Retrieve all the Notion-side vacations."""
        return cast(Iterable[VacationRow], self._collection.load_all(self._DISCRIMINANT))

    def load_vacation_by_id(self, ref_id: EntityId) -> VacationRow:
        """Retrieve the Notion-side vacation associated with a particular entity."""
        return cast(VacationRow, self._collection.load_by_id(self._DISCRIMINANT, ref_id))

    def save_vacation(self, new_vacation_row: VacationRow) -> None:
        """Update a Notion-side vacation with new data."""
        self._collection.save(self._DISCRIMINANT, new_vacation_row)

    def hard_remove_vacation(self, ref_id: EntityId) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        self._collection.hard_remove(self._DISCRIMINANT, ref_id)

    @staticmethod
    def get_page_name() -> str:
        """Get the name for the page."""
        return VacationsCollection._PAGE_NAME

    @staticmethod
    def get_notion_schema() -> JSONDictType:
        """Get the Notion schema for the collection."""
        return VacationsCollection._SCHEMA

    @staticmethod
    def get_view_schemas() -> Dict[str, JSONDictType]:
        """Get the Notion view schemas for the collection."""
        return {
            "database_view_id": VacationsCollection._DATABASE_VIEW_SCHEMA
        }

    @staticmethod
    @typing.no_type_check
    def merge_notion_schemas(old_schema: JSONDictType, new_schema: JSONDictType) -> JSONDictType:
        """Merge an old and new schema for the collection."""
        combined_schema: JSONDictType = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        for (schema_item_name, schema_item_raw) in new_schema.items():
            schema_item = schema_item_raw
            if schema_item["type"] == "select" or schema_item["type"] == "multi_select":
                if schema_item_name in old_schema:
                    old_v = old_schema[schema_item_name]

                    combined_schema[schema_item_name] = {
                        "name": schema_item["name"],
                        "type": schema_item["type"],
                        "options": []
                    }

                    for option in cast(Dict[str, str], schema_item["options"]):
                        old_option = next((old_o for old_o in old_v["options"] if old_o["value"] == option["value"]),
                                          None)
                        if old_option is not None:
                            combined_schema[schema_item_name]["options"].append({
                                "color": option["color"],
                                "value": option["value"],
                                "id": old_option["id"]
                            })
                        else:
                            combined_schema[schema_item_name]["options"].append(option)
                else:
                    combined_schema[schema_item_name] = schema_item
            else:
                combined_schema[schema_item_name] = schema_item

        return combined_schema

    @staticmethod
    def copy_row_to_notion_row(
            client: NotionClient, row: VacationRow, notion_row: CollectionRowBlock,
            **kwargs: NotionCollectionKWArgsType) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        # pylint: disable=unused-argument
        notion_row.title = row.name
        notion_row.archived = row.archived
        notion_row.start_date = row.start_date
        notion_row.end_date = row.end_date
        notion_row.ref_id = row.ref_id

        return notion_row

    @staticmethod
    def copy_notion_row_to_row(vacation_notion_row: CollectionRowBlock) -> VacationRow:
        """Transform the live system data to something suitable for basic storage."""
        return VacationRow(
            notion_id=vacation_notion_row.id,
            name=vacation_notion_row.title,
            archived=vacation_notion_row.archived or False,
            start_date=pendulum.parse(str(vacation_notion_row.start_date.start))
            if vacation_notion_row.start_date else None,
            end_date=pendulum.parse(str(vacation_notion_row.end_date.start))
            if vacation_notion_row.end_date else None,
            ref_id=vacation_notion_row.ref_id)
