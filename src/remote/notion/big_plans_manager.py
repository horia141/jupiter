"""The centralised point for interacting with Notion big plans."""
import logging
import uuid
from dataclasses import dataclass
from typing import Final, ClassVar, cast, Dict, Optional, Iterable

from notion.collection import CollectionRowBlock

from domain.big_plans.big_plan_status import BigPlanStatus
from domain.common.adate import ADate
from domain.common.entity_name import EntityName
from domain.common.timestamp import Timestamp
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from models.framework import BaseNotionRow, EntityId, JSONDictType, NotionId
from remote.notion.common import NotionLockKey, NotionPageLink, NotionCollectionLink, format_name_for_option
from remote.notion.infra.client import NotionClient, NotionCollectionSchemaProperties, NotionFieldProps, NotionFieldShow
from remote.notion.infra.collections_manager import CollectionsManager
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class BigPlanNotionCollection(BaseNotionRow):
    """A big plan collection on Notion side."""


@dataclass()
class BigPlanNotionRow(BaseNotionRow):
    """A big plan on Notion side."""

    name: str
    archived: bool
    status: Optional[str]
    due_date: Optional[ADate]
    last_edited_time: Timestamp


class NotionBigPlansManager:
    """The centralised point for interacting with Notion big plans."""

    _KEY: ClassVar[str] = "big-plans"

    _PAGE_NAME: ClassVar[str] = "Big Plans"

    _STATUS: ClassVar[JSONDictType] = {
        "Not Started": {
            "name": BigPlanStatus.NOT_STARTED.for_notion(),
            "color": "orange",
            "in_board": True
        },
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
        "due-date": {
            "name": "Due Date",
            "type": "date"
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
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
        NotionFieldProps("status", NotionFieldShow.SHOW),
        NotionFieldProps("due-date", NotionFieldShow.SHOW),
        NotionFieldProps("archived", NotionFieldShow.SHOW),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

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
        }, {
            "property": "last-edited-time",
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
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": True
            }]
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

    def upsert_big_plan_collection(
            self, project_ref_id: EntityId, parent_page_link: NotionPageLink) -> BigPlanNotionCollection:
        """Upsert the Notion-side big plan."""
        collection_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            parent_page=parent_page_link,
            name=self._PAGE_NAME,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "kanban_all_view_id": NotionBigPlansManager._KANBAN_ALL_VIEW_SCHEMA,
                "database_view_id": NotionBigPlansManager._DATABASE_VIEW_SCHEMA
            })

        return BigPlanNotionCollection(
            ref_id=str(project_ref_id),
            notion_id=collection_link.collection_id)

    def remove_big_plans_collection(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""
        return self._collections_manager.remove_collection(NotionLockKey(f"{self._KEY}:{project_ref_id}"))

    def upsert_big_plan(
            self, project_ref_id: EntityId, inbox_collection_link: NotionCollectionLink, name: EntityName,
            archived: bool, due_date: Optional[ADate], status: str, ref_id: EntityId) -> BigPlanNotionRow:
        """Upsert a big plan."""
        new_row = BigPlanNotionRow(
            name=str(name),
            archived=archived,
            status=status,
            due_date=due_date,
            last_edited_time=self._time_provider.get_current_time(),
            ref_id=str(ref_id),
            notion_id=cast(NotionId, None))
        self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            new_row=new_row,
            copy_row_to_notion_row=lambda c, r, nr: self._copy_row_to_notion_row(c, r, nr, inbox_collection_link))
        return new_row

    def link_local_and_notion_entries(self, project_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries(
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def load_all_big_plans(self, project_ref_id: EntityId) -> Iterable[BigPlanNotionRow]:
        """Retrieve all the Notion-side big plans."""
        return self._collections_manager.load_all(
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def load_big_plan(self, project_ref_id: EntityId, ref_id: EntityId) -> BigPlanNotionRow:
        """Retrieve the Notion-side big plan associated with a particular entity."""
        return self._collections_manager.load(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def archive_big_plan(self, project_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a particular big plans."""
        self._collections_manager.quick_archive(
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            key=NotionLockKey(f"{ref_id}"))

    def save_big_plan(
            self, project_ref_id: EntityId, ref_id: EntityId, new_big_plan_row: BigPlanNotionRow,
            inbox_collection_link: Optional[NotionCollectionLink] = None) -> BigPlanNotionRow:
        """Update the Notion-side big plan with new data."""
        return self._collections_manager.save(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"),
            row=new_big_plan_row,
            copy_row_to_notion_row=lambda c, r, nr: self._copy_row_to_notion_row(c, r, nr, inbox_collection_link))

    def load_all_saved_big_plans_notion_ids(self, project_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""
        return self._collections_manager.load_all_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"))

    def load_all_saved_big_plans_ref_ids(self, project_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the big plans tasks."""
        return self._collections_manager.load_all_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"))

    def drop_all_big_plans(self, project_ref_id: EntityId) -> None:
        """Remove all big plans Notion-side."""
        self._collections_manager.drop_all(collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"))

    def hard_remove_big_plan(self, project_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        self._collections_manager.hard_remove(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{project_ref_id}"))

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: BigPlanNotionRow, notion_row: CollectionRowBlock,
            inbox_collection_link: Optional[NotionCollectionLink]) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.archived = row.archived
            notion_row.status = row.status
            notion_row.due_date = row.due_date.to_notion(self._global_properties.timezone) if row.due_date else None
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = row.ref_id

        # Create structure for the big plan.

        if inbox_collection_link:
            LOGGER.info(f"Creating views structure for plan {notion_row}")

            client.attach_view_block_as_child_of_block(
                notion_row, 0, inbox_collection_link.collection_id,
                self._get_view_schema_for_big_plan_desc(format_name_for_option(EntityName(row.name))))

        return notion_row

    def _copy_notion_row_to_row(self, big_plan_notion_row: CollectionRowBlock) -> BigPlanNotionRow:
        """Transform the live system data to something suitable for basic storage."""
        # pylint: disable=no-self-use
        return BigPlanNotionRow(
            notion_id=big_plan_notion_row.id,
            name=big_plan_notion_row.title,
            archived=big_plan_notion_row.archived,
            status=big_plan_notion_row.status,
            due_date=ADate.from_notion(self._global_properties.timezone, big_plan_notion_row.due_date)
            if big_plan_notion_row.due_date else None,
            last_edited_time=
            Timestamp.from_notion(big_plan_notion_row.last_edited_time),
            ref_id=big_plan_notion_row.ref_id)

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
                    }, {
                        "property": "source",
                        "filter": {
                            "operator": "enum_is",
                            "value": {
                                "type": "exact",
                                "value": InboxTaskSource.BIG_PLAN.for_notion()
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
                    "property": "actionable-date",
                    "visible": True
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
