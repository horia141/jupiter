"""The collection for big plans."""
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
import typing
from typing import Final, Optional, Dict, ClassVar, Iterable, cast

import pendulum

from notion.collection import CollectionRowBlock

import remote.notion.common
from models.basic import EntityId, BigPlanStatus
from remote.notion.client import NotionClient
from remote.notion.collection import NotionCollection, BasicRowType, NotionCollectionKWArgsType
from remote.notion.common import NotionId, NotionPageLink, NotionCollectionLink
from remote.notion.connection import NotionConnection
from utils.storage import JSONDictType

LOGGER = logging.getLogger(__name__)


@dataclass()
class BigPlanRow(BasicRowType):
    """A big plan on Notion side."""

    name: str
    archived: bool
    status: Optional[str]
    due_date: Optional[pendulum.DateTime]


class BigPlansCollection:
    """A collection on Notion side for big plans."""

    _LOCK_FILE_PATH: ClassVar[Path] = Path("/data/big-plans.lock.yaml")

    _PAGE_NAME: ClassVar[str] = "Big Plans"

    _STATUS: ClassVar[JSONDictType] = {
        "Accepted": {
            "name": BigPlanStatus.ACCEPTED.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "In Progress": {
            "name": BigPlanStatus.IN_PROGRESS.for_notion(),
            "color": "blue",
            "in_board": True
        },
        "Blocked": {
            "name": BigPlanStatus.BLOCKED.for_notion(),
            "color": "yellow",
            "in_board": True
        },
        "Not Done": {
            "name": BigPlanStatus.NOT_DONE.for_notion(),
            "color": "red",
            "in_board": True
        },
        "Done": {
            "name": BigPlanStatus.DONE.for_notion(),
            "color": "green",
            "in_board": True
        }
    }

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "status": {
            "name": "Status",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _STATUS.values()]
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        },
        "due-date": {
            "name": "Due Date",
            "type": "date"
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "inboxid": {
            "name": "Inbox Id Ref",
            "type": "text"
        }
    }

    _FORMAT: ClassVar[JSONDictType] = {
        "board_groups": [{
            "property": "status",
            "type": "select",
            "value": cast(Dict[str, str], v)["name"],
            "hidden": not cast(Dict[str, bool], v)["in_board"]
        } for v in _STATUS.values()] + [{
            "property": "status",
            "type": "select",
            "hidden": True
        }],
        "board_groups2": [{
            "property": "status",
            "value": {
                "type": "select",
                "value": cast(Dict[str, str], v)["name"]
            },
            "hidden": not cast(Dict[str, bool], v)["in_board"]
        } for v in _STATUS.values()] + [{
            "property": "status",
            "value": {
                "type": "select"
            },
            "hidden": True
        }],
        "board_properties": [{
            "property": "status",
            "visible": False
        }, {
            "property": "due-date",
            "visible": True
        }, {
            "property": "archived",
            "visible": False
        }],
        "board_cover_size": "small"
    }

    _KANBAN_ALL_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban All",
        "type": "board",
        "query2": {
            "group_by": "status",
            "filter_operator": "and",
            "aggregations": [{
                "aggregator": "count"
            }],
            "sort": [{
                "property": "due-date",
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
        },
        "format": _FORMAT
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
                "property": "ref-id",
                "visible": False
            }, {
                "width": 100,
                "property": "status",
                "visible": True
            }, {
                "width": 100,
                "property": "due-date",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }]
        }
    }

    _collection: Final[NotionCollection[BigPlanRow]]

    def __init__(self, connection: NotionConnection) -> None:
        """Constructor."""
        self._collection = NotionCollection[BigPlanRow](connection, self._LOCK_FILE_PATH, self)

    def __enter__(self) -> 'BigPlansCollection':
        """Enter context."""
        self._collection.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._collection.exit_save()

    def upsert_big_plans_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Create the Notion-side structure for this collection."""
        return self._collection.upsert_structure(project_ref_id, parent_page)

    def remove_big_plans_structure(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""
        return self._collection.remove_structure(project_ref_id)

    def create_big_plan(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink, name: str,
            archived: bool, due_date: Optional[pendulum.DateTime], status: str, ref_id: EntityId) -> BigPlanRow:
        """Create a big plan."""
        new_big_plan_row = BigPlanRow(
            notion_id=NotionId("FAKE-FAKE-FAKE"),
            name=name,
            archived=archived,
            status=status,
            due_date=due_date,
            ref_id=ref_id)
        return cast(BigPlanRow, self._collection.create(
            project_ref_id, new_big_plan_row, inbox_collection_link=inbox_collection_link))

    def link_local_and_notion_entries(self, project_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collection.link_local_and_notion_entries(project_ref_id, ref_id, notion_id)

    def archive_big_plan(self, project_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a particular big plans."""
        self._collection.archive(project_ref_id, ref_id)

    def load_all_big_plans(self, project_ref_id: EntityId) -> Iterable[BigPlanRow]:
        """Retrieve all the Notion-side big plans."""
        return cast(Iterable[BigPlanRow], self._collection.load_all(project_ref_id))

    def load_big_plan(self, project_ref_id: EntityId, ref_id: EntityId) -> BigPlanRow:
        """Retrieve the Notion-side big plan associated with a particular entity."""
        return cast(BigPlanRow, self._collection.load(project_ref_id, ref_id))

    def save_big_plan(
            self, project_ref_id: EntityId, new_big_plan_row: BigPlanRow,
            inbox_collection_link: Optional[NotionCollectionLink] = None) -> BigPlanRow:
        """Update the Notion-side big plan with new data."""
        return cast(
            BigPlanRow,
            self._collection.save(project_ref_id, new_big_plan_row, inbox_collection_link=inbox_collection_link))

    def hard_remove_big_plan(self, project_ref_id: EntityId, ref_id: EntityId) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        self._collection.hard_remove(project_ref_id, ref_id)

    @staticmethod
    def get_page_name() -> str:
        """Get the name for the page."""
        return BigPlansCollection._PAGE_NAME

    @staticmethod
    def get_notion_schema() -> JSONDictType:
        """Get the Notion schema for the collection."""
        return BigPlansCollection._SCHEMA

    @staticmethod
    def get_view_schemas() -> Dict[str, JSONDictType]:
        """Get the Notion view schemas for the collection."""
        return {
            "kanban_all_view_id": BigPlansCollection._KANBAN_ALL_VIEW_SCHEMA,
            "database_view_id": BigPlansCollection._DATABASE_VIEW_SCHEMA
        }

    @staticmethod
    @typing.no_type_check
    def merge_notion_schemas(old_schema: JSONDictType, new_schema: JSONDictType) -> JSONDictType:
        """Merge an old and new schema for the collection."""
        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        for (schema_item_name, schema_item) in new_schema.items():
            if schema_item["type"] == "select" or schema_item["type"] == "multi_select":
                if schema_item_name in old_schema:
                    old_v = old_schema[schema_item_name]

                    combined_schema[schema_item_name] = {
                        "name": schema_item["name"],
                        "type": schema_item["type"],
                        "options": []
                    }

                    for option in schema_item["options"]:
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
            client: NotionClient, row: BigPlanRow, notion_row: CollectionRowBlock,
            **kwargs: NotionCollectionKWArgsType) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        inbox_collection_link = cast(NotionCollectionLink, kwargs.get("inbox_collection_link", None))

        # Create fields of the big plan row.
        notion_row.title = row.name
        notion_row.archived = row.archived
        notion_row.status = row.status
        notion_row.due_date = row.due_date
        notion_row.ref_id = row.ref_id

        # Create structure for the big plan.

        if inbox_collection_link:
            LOGGER.info(f"Creating views structure for plan {notion_row}")

            client.attach_view_block_as_child_of_block(
                notion_row, 0, inbox_collection_link.collection_id,
                BigPlansCollection._get_view_schema_for_big_plan_desc(
                    remote.notion.common.format_name_for_option(row.name)))

        return notion_row

    @staticmethod
    def copy_notion_row_to_row(inbox_task_notion_row: CollectionRowBlock) -> BigPlanRow:
        """Transform the live system data to something suitable for basic storage."""
        return BigPlanRow(
            notion_id=inbox_task_notion_row.id,
            name=inbox_task_notion_row.title,
            archived=inbox_task_notion_row.archived,
            status=inbox_task_notion_row.status,
            due_date=pendulum.parse(str(inbox_task_notion_row.due_date.start))
            if inbox_task_notion_row.due_date else None,
            ref_id=inbox_task_notion_row.ref_id)

    @staticmethod
    def _get_view_schema_for_big_plan_desc(big_plan_name: str) -> JSONDictType:
        """Get the view schema for a big plan details view."""
        return {
            "name": "Inbox Tasks",
            "query2": {
                "filter_operator": "and",
                "sort": [{
                    "property": "status",
                    "direction": "ascending"
                }, {
                    "property": "due-date",
                    "direction": "ascending"
                }],
                "filter": {
                    "operator": "and",
                    "filters": [{
                        "property": "bigplan2",
                        "filter": {
                            "operator": "enum_is",
                            "value": {
                                "type": "exact",
                                "value": big_plan_name
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
                    "property": "status",
                    "visible": True
                }, {
                    "width": 100,
                    "property": "bigplan2",
                    "visible": False
                }, {
                    "width": 100,
                    "property": "due-date",
                    "visible": True
                }, {
                    "width": 100,
                    "property": "eisen",
                    "visible": True
                }, {
                    "width": 100,
                    "property": "difficulty",
                    "visible": True
                }, {
                    "width": 100,
                    "property": "fromscript",
                    "visible": False
                }, {
                    "width": 100,
                    "property": "period",
                    "visible": False
                }, {
                    "width": 100,
                    "property": "timeline",
                    "visible": False
                }]
            }
        }
