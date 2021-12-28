"""The centralised point for interacting with Notion recurring tasks."""
import logging
import uuid
from typing import Optional, ClassVar, Final, cast, Dict, Iterable

from notion.collection import CollectionRowBlock

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager, \
    NotionRecurringTaskCollectionNotFoundError, NotionRecurringTaskNotFoundError
from jupiter.domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from jupiter.domain.recurring_tasks.notion_recurring_task_collection import NotionRecurringTaskCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey, NotionPageLink, clean_eisenhower
from jupiter.remote.notion.infra.client import NotionFieldProps, NotionFieldShow, NotionClient
from jupiter.remote.notion.infra.collections_manager import CollectionsManager, NotionCollectionItemNotFoundError, \
    NotionCollectionNotFoundError
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionRecurringTasksManager(RecurringTaskNotionManager):
    """The centralised point for interacting with Notion recurring tasks."""

    _KEY: ClassVar[str] = "recurring-tasks"

    _PAGE_NAME: ClassVar[str] = "Recurring Tasks"

    _PERIOD: ClassVar[JSONDictType] = {
        "Daily": {
            "name": RecurringTaskPeriod.DAILY.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "Weekly": {
            "name": RecurringTaskPeriod.WEEKLY.for_notion(),
            "color": "green",
            "in_board": True
        },
        "Monthly": {
            "name": RecurringTaskPeriod.MONTHLY.for_notion(),
            "color": "yellow",
            "in_board": True
        },
        "Quarterly": {
            "name": RecurringTaskPeriod.QUARTERLY.for_notion(),
            "color": "blue",
            "in_board": True
        },
        "Yearly": {
            "name": RecurringTaskPeriod.YEARLY.for_notion(),
            "color": "red",
            "in_board": True
        }
    }

    _TYPE: ClassVar[JSONDictType] = {
        "Chore": {
            "name": RecurringTaskType.CHORE.for_notion(),
            "color": "green",
            "in_board": True
        },
        "Habit": {
            "name": RecurringTaskType.HABIT.for_notion(),
            "color": "blue",
            "in_board": True
        }
    }

    _EISENHOWER: ClassVar[JSONDictType] = {
        "Urgent": {
            "name": Eisen.URGENT.for_notion(),
            "color": "red"
        },
        "Important": {
            "name": Eisen.IMPORTANT.for_notion(),
            "color": "blue"
        }
    }

    _DIFFICULTY = {
        "Easy": {
            "name": Difficulty.EASY.for_notion(),
            "color": "blue"
        },
        "Medium": {
            "name": Difficulty.MEDIUM.for_notion(),
            "color": "green"
        },
        "Hard": {
            "name": Difficulty.HARD.for_notion(),
            "color": "purple"
        }
    }

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "period": {
            "name": "Period",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _PERIOD.values()]
        },
        "the-type": {
            "name": "The Type",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _TYPE.values()]
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "eisen": {
            "name": "Eisenhower",
            "type": "multi_select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _EISENHOWER.values()]
        },
        "difficulty": {
            "name": "Difficulty",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _DIFFICULTY.values()]
        },
        "actionable-from-day": {
            "name": "Actionable From Day",
            "type": "number",
        },
        "actionable-from-month": {
            "name": "Actionable From Month",
            "type": "number",
        },
        "due-at-time": {
            "name": "Due At Time",
            "type": "text",
        },
        "due-at-day": {
            "name": "Due At Day",
            "type": "number",
        },
        "due-at-month": {
            "name": "Due At Month",
            "type": "number",
        },
        "suspended": {
            "name": "Suspended",
            "type": "checkbox",
        },
        "must-do": {
            "name": "Must Do",
            "type": "checkbox"
        },
        "skip-rule": {
            "name": "Skip Rule",
            "type": "text"
        },
        "start-at-date": {
            "name": "Start At Date",
            "type": "date"
        },
        "end-at-date": {
            "name": "End At Date",
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

    _SCHEMA_PROPERTIES = [
        NotionFieldProps(name="title", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="period", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="the-type", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="eisen", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="difficulty", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="actionable-from-month", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="actionable-from-day", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-at-month", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-at-day", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-at-time", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="skip-rule", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="start-at-date", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="end-at-date", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="suspended", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="must-do", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="archived", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="ref-id", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="last-edited-time", show=NotionFieldShow.SHOW)
    ]

    _KANBAN_ALL_VIEW_SCHEMA: JSONDictType = {
        "name": "Kanban",
        "type": "board",
        "query2": {
            "group_by": "period",
            "filter_operator": "and",
            "aggregations": [{
                "aggregator": "count"
            }],
            "sort": [{
                "property": "suspended",
                "direction": "ascending"
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "due-at-month",
                "direction": "ascending"
            }, {
                "property": "due-at-day",
                "direction": "ascending"
            }, {
                "property": "due-at-time",
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
        "format": {
            "board_groups": [{
                "property": "period",
                "type": "select",
                "value": cast(Dict[str, str], v)["name"],
                "hidden": not cast(Dict[str, bool], v)["in_board"]
            } for v in _PERIOD.values()],
            "board_groups2": [{
                "property": "period",
                "value": {
                    "type": "select",
                    "value": cast(Dict[str, str], v)["name"]
                },
                "hidden": not cast(Dict[str, bool], v)["in_board"]
            } for v in _PERIOD.values()],
            "board_properties": [{
                "property": "period",
                "visible": False
            }, {
                "property": "the-type",
                "visible": True
            }, {
                "property": "archived",
                "visible": False,
            }, {
                "property": "eisen",
                "visible": True
            }, {
                "property": "difficulty",
                "visible": True
            }, {
                "property": "actionable-from-day",
                "visible": True
            }, {
                "property": "actionable-from-month",
                "visible": True
            }, {
                "property": "due-at-time",
                "visible": True
            }, {
                "property": "due-at-day",
                "visible": True
            }, {
                "property": "due-at-month",
                "visible": True
            }, {
                "property": "suspended",
                "visible": True
            }, {
                "property": "must-do",
                "visible": False
            }, {
                "property": "skip-rule",
                "visible": False
            }, {
                "property": "start-at-date",
                "visible": False
            }, {
                "property": "end-at-date",
                "visible": False
            }, {
                "property": "last-edited-time",
                "visible": False
            }, {
                "property": "ref-id",
                "visible": False
            }],
            "board_cover_size": "small"
        }
    }

    _DATABASE_VIEW_SCHEMA: JSONDictType = {
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
                "visible": True
            }, {
                "width": 100,
                "property": "period",
                "visible": True
            }, {
                "width": 100,
                "property": "the-type",
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
                "property": "actionable-from-day",
                "visible": True
            }, {
                "width": 100,
                "property": "actionable-from-month",
                "visible": True
            }, {
                "width": 100,
                "property": "due-at-time",
                "visible": True
            }, {
                "width": 100,
                "property": "due-at-day",
                "visible": True
            }, {
                "width": 100,
                "property": "due-at-month",
                "visible": True
            }, {
                "width": 100,
                "property": "suspended",
                "visible": True
            }, {
                "width": 100,
                "property": "must-do",
                "visible": True
            }, {
                "width": 100,
                "property": "skip-rule",
                "visible": True
            }, {
                "width": 100,
                "property": "start-at-date",
                "visible": True
            }, {
                "width": 100,
                "property": "end-at-date",
                "visible": True
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": False
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

    def upsert_recurring_task_collection(
            self, notion_project: NotionProject,
            recurring_task_collection: NotionRecurringTaskCollection) -> NotionRecurringTaskCollection:
        """Upsert the Notion-side recurring task."""
        collection_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{recurring_task_collection.ref_id}"),
            parent_page=NotionPageLink(notion_project.notion_id),
            name=self._PAGE_NAME,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "kanban_all_view_id": NotionRecurringTasksManager._KANBAN_ALL_VIEW_SCHEMA,
                "database_view_id": NotionRecurringTasksManager._DATABASE_VIEW_SCHEMA
            })

        return NotionRecurringTaskCollection(
            notion_id=collection_link.collection_id,
            ref_id=recurring_task_collection.ref_id)

    def load_recurring_task_collection(self, ref_id: EntityId) -> NotionRecurringTaskCollection:
        """Retrieve the Notion-side recurring task collection."""
        try:
            recurring_task_collection_link = self._collections_manager.load_collection(
                key=NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionRecurringTaskCollectionNotFoundError(
                f"Could not find recurring task collection with id {ref_id} locally") from err

        return NotionRecurringTaskCollection(
            ref_id=ref_id,
            notion_id=recurring_task_collection_link.collection_id)

    def remove_recurring_tasks_collection(self, ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""
        try:
            return self._collections_manager.remove_collection(NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionRecurringTaskCollectionNotFoundError(
                f"Notion recurring task collection with id {ref_id} could not be found") \
                from err

    def upsert_recurring_task(
            self, recurring_task_collection_ref_id: EntityId, recurring_task: NotionRecurringTask,
            inbox_collection_link: NotionInboxTaskCollection) -> NotionRecurringTask:
        """Upsert a recurring task."""
        return self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{recurring_task.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"),
            new_row=recurring_task,
            copy_row_to_notion_row=lambda c, r, nr: self._copy_row_to_notion_row(c, r, nr, inbox_collection_link))

    def save_recurring_task(
            self, recurring_task_collection_ref_id: EntityId, recurring_task: NotionRecurringTask,
            inbox_collection_link: Optional[NotionInboxTaskCollection] = None) -> NotionRecurringTask:
        """Update the Notion-side recurring task with new data."""
        try:
            return self._collections_manager.save_collection_item(
                key=NotionLockKey(f"{recurring_task.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"),
                row=recurring_task,
                copy_row_to_notion_row=lambda c, r, nr: self._copy_row_to_notion_row(c, r, nr, inbox_collection_link))
        except NotionCollectionItemNotFoundError as err:
            raise NotionRecurringTaskNotFoundError(
                f"Notion recurring task with id {recurring_task.ref_id} could not be found") from err

    def load_recurring_task(self, recurring_task_collection_ref_id: EntityId, ref_id: EntityId) -> NotionRecurringTask:
        """Retrieve the Notion-side recurring task associated with a particular entity."""
        try:
            return self._collections_manager.load_collection_item(
                key=NotionLockKey(f"{ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"),
                copy_notion_row_to_row=self._copy_notion_row_to_row)
        except NotionCollectionItemNotFoundError as err:
            raise NotionRecurringTaskNotFoundError(
                f"Notion recurring task with id {ref_id} could not be found") from err

    def load_all_recurring_tasks(
            self, recurring_task_collection_ref_id: EntityId) -> Iterable[NotionRecurringTask]:
        """Retrieve all the Notion-side recurring tasks."""
        return self._collections_manager.load_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def remove_recurring_task(self, recurring_task_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"))
        except NotionCollectionItemNotFoundError as err:
            raise NotionRecurringTaskNotFoundError(
                f"Notion recurring task with id {ref_id} could not be found") from err

    def drop_all_recurring_tasks(self, recurring_task_collection_ref_id: EntityId) -> None:
        """Remove all recurring tasks Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"))

    def link_local_and_notion_recurring_task(
            self, recurring_task_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def load_all_saved_recurring_tasks_notion_ids(
            self, recurring_task_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"))

    def load_all_saved_recurring_tasks_ref_ids(self, recurring_task_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the recurring tasks tasks."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{recurring_task_collection_ref_id}"))

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionRecurringTask, notion_row: CollectionRowBlock,
            inbox_collection_link: Optional[NotionInboxTaskCollection]) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        if row.ref_id is None:
            raise Exception(f"Recurring task row '{row.name}' which is synced must have a ref id")

        with client.with_transaction():
            notion_row.title = row.name
            notion_row.archived = row.archived
            notion_row.period = row.period
            notion_row.the_type = row.the_type
            notion_row.eisenhower = row.eisen
            notion_row.difficulty = row.difficulty
            notion_row.actionable_from_day = row.actionable_from_day
            notion_row.actionable_from_month = row.actionable_from_month
            notion_row.due_at_time = row.due_at_time
            notion_row.due_at_day = row.due_at_day
            notion_row.due_at_month = row.due_at_month
            notion_row.suspended = row.suspended
            notion_row.skip_rule = row.skip_rule
            notion_row.must_do = row.must_do
            notion_row.start_at_date = \
                row.start_at_date.to_notion(self._global_properties.timezone) if row.start_at_date else None
            notion_row.end_at_date = \
                row.end_at_date.to_notion(self._global_properties.timezone) if row.end_at_date else None
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = row.ref_id

        if inbox_collection_link:
            LOGGER.info(f"Creating views structure for recurring task {notion_row}")

            client.attach_view_block_as_child_of_block(
                notion_row, 0, inbox_collection_link.notion_id,
                self._get_view_schema_for_recurring_tasks_desc(row.ref_id))

        return notion_row

    def _copy_notion_row_to_row(self, recurring_task_notion_row: CollectionRowBlock) -> NotionRecurringTask:
        """Transform the live system data to something suitable for basic storage."""
        return NotionRecurringTask(
            notion_id=NotionId.from_raw(recurring_task_notion_row.id),
            name=recurring_task_notion_row.title,
            archived=recurring_task_notion_row.archived,
            period=recurring_task_notion_row.period,
            the_type=recurring_task_notion_row.the_type,
            eisen=clean_eisenhower(recurring_task_notion_row.eisenhower),
            difficulty=recurring_task_notion_row.difficulty,
            actionable_from_day=recurring_task_notion_row.actionable_from_day,
            actionable_from_month=recurring_task_notion_row.actionable_from_month,
            due_at_time=recurring_task_notion_row.due_at_time,
            due_at_day=recurring_task_notion_row.due_at_day,
            due_at_month=recurring_task_notion_row.due_at_month,
            suspended=recurring_task_notion_row.suspended,
            skip_rule=recurring_task_notion_row.skip_rule,
            must_do=recurring_task_notion_row.must_do,
            start_at_date=ADate.from_notion(self._global_properties.timezone, recurring_task_notion_row.start_at_date)
            if recurring_task_notion_row.start_at_date else None,
            end_at_date=ADate.from_notion(self._global_properties.timezone, recurring_task_notion_row.end_at_date)
            if recurring_task_notion_row.end_at_date else None,
            last_edited_time=
            Timestamp.from_notion(recurring_task_notion_row.last_edited_time),
            ref_id=recurring_task_notion_row.ref_id)

    @staticmethod
    def _get_view_schema_for_recurring_tasks_desc(recurring_task_ref_id: str) -> JSONDictType:
        """Get the view schema for a recurring task details view."""
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
                        "property": "recurring-task-ref-id",
                        "filter": {
                            "operator": "string_is",
                            "value": {
                                "type": "exact",
                                "value": recurring_task_ref_id
                            }
                        }
                    }, {
                        "property": "source",
                        "filter": {
                            "operator": "enum_is",
                            "value": {
                                "type": "exact",
                                "value": InboxTaskSource.RECURRING_TASK.for_notion()
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
