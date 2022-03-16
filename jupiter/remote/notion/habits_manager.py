"""The centralised point for interacting with Notion habits."""
import copy
import hashlib
import logging
import uuid
from typing import Optional, ClassVar, Final, cast, Dict, Iterable

from notion.collection import CollectionRowBlock

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager, \
    NotionHabitNotFoundError
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey, format_name_for_option
from jupiter.remote.notion.infra.client import NotionFieldProps, NotionFieldShow, NotionClient
from jupiter.remote.notion.infra.collections_manager \
    import NotionCollectionsManager, NotionCollectionItemNotFoundError
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionHabitsManager(HabitNotionManager):
    """The centralised point for interacting with Notion habits."""

    _KEY: ClassVar[str] = "habits"
    _PAGE_NAME: ClassVar[str] = "Habits"
    _PAGE_ICON: ClassVar[str] = "💪"

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

    _EISENHOWER: ClassVar[JSONDictType] = {
        "Important-And-Urgent": {
            "name": Eisen.IMPORTANT_AND_URGENT.for_notion(),
            "color": "green"
        },
        "Urgent": {
            "name": Eisen.URGENT.for_notion(),
            "color": "red"
        },
        "Important": {
            "name": Eisen.IMPORTANT.for_notion(),
            "color": "blue"
        },
        "Regular": {
            "name": Eisen.REGULAR.for_notion(),
            "color": "orange"
        }
    }

    _DIFFICULTY: ClassVar[JSONDictType] = {
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
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "project-ref-id": {
            "name": "Project Id",
            "type": "text"
        },
        "project-name": {
            "name": "Project",
            "type": "select",
            "options": [{"color": "gray", "id": str(uuid.uuid4()), "value": "None"}]
        },
        "eisen": {
            "name": "Eisenhower",
            "type": "select",
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
        "skip-rule": {
            "name": "Skip Rule",
            "type": "text"
        },
        "repeats-in-period": {
            "name": "Repeats In Period",
            "type": "number"
        },
        "suspended": {
            "name": "Suspended",
            "type": "checkbox",
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
        NotionFieldProps(name="project-ref-id", show=NotionFieldShow.HIDE),
        NotionFieldProps(name="project-name", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="eisen", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="difficulty", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="actionable-from-month", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="actionable-from-day", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-at-month", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-at-day", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-at-time", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="skip-rule", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="repeats-in-period", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="suspended", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="archived", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="ref-id", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="last-edited-time", show=NotionFieldShow.SHOW)
    ]

    _DATABASE_BY_PROJECT_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "List By Project",
        "type": "table",
        "query2": {
            "sort": [{
                "property": "suspended",
                "direction": "ascending"
            }, {
                "property": "period",
                "direction": "ascending"
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }]
        },
        "format": {
            "collection_group_by": {
                "property": "project-name",
                "type": "select",
                "sort": {
                    "type": "manual"
                }
            },
            "table_properties": [{
                "width": 400,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "period",
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
                "width": 50,
                "property": "actionable-from-day",
                "visible": True
            }, {
                "width": 50,
                "property": "actionable-from-month",
                "visible": True
            }, {
                "width": 50,
                "property": "due-at-time",
                "visible": True
            }, {
                "width": 50,
                "property": "due-at-day",
                "visible": True
            }, {
                "width": 50,
                "property": "due-at-month",
                "visible": True
            }, {
                "width": 100,
                "property": "skip-rule",
                "visible": True
            }, {
                "width": 100,
                "property": "repeats-in-period",
                "visible": True
            }, {
                "width": 50,
                "property": "suspended",
                "visible": True
            }, {
                "width": 50,
                "property": "archived",
                "visible": True
            }, {
                "width": 100,
                "property": "project-ref-id",
                "visible": False
            }, {
                "width": 100,
                "property": "project-name",
                "visible": False
            }, {
                "width": 100,
                "property": "last-edited-time",
                "visible": False
            }, {
                "width": 100,
                "property": "ref-id",
                "visible": False
            }]
        }
    }

    _KANBAN_ALL_VIEW_SCHEMA: ClassVar[JSONDictType] = {
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
                            "value": True
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
                "property": "archived",
                "visible": False,
            }, {
                "property": "project-ref-id",
                "visible": False
            }, {
                "property": "project-name",
                "visible": True
            }, {
                "property": "eisen",
                "visible": True
            }, {
                "property": "difficulty",
                "visible": True
            }, {
                "property": "actionable-from-day",
                "visible": False
            }, {
                "property": "actionable-from-month",
                "visible": False
            }, {
                "property": "due-at-time",
                "visible": False
            }, {
                "property": "due-at-day",
                "visible": False
            }, {
                "property": "due-at-month",
                "visible": False
            }, {
                "property": "skip-rule",
                "visible": False
            }, {
                "property": "repeats-in-period",
                "visible": False
            }, {
                "property": "suspended",
                "visible": True
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
                "property": "project-ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "project-name",
                "visible": True
            }, {
                "width": 100,
                "property": "period",
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
                "property": "skip-rule",
                "visible": True
            }, {
                "width": 100,
                "property": "repeats-in-period",
                "visible": True
            }, {
                "width": 100,
                "property": "suspended",
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
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            collections_manager: NotionCollectionsManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._collections_manager = collections_manager

    def upsert_trunk(self, parent: NotionWorkspace, trunk: NotionHabitCollection) -> None:
        """Upsert the Notion-side habit."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{trunk.ref_id}"),
            parent_page_notion_id=parent.notion_id,
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                ("database_by_project_view_id", NotionHabitsManager._DATABASE_BY_PROJECT_VIEW_SCHEMA),
                ("kanban_all_view_id", NotionHabitsManager._KANBAN_ALL_VIEW_SCHEMA),
                ("database_view_id", NotionHabitsManager._DATABASE_VIEW_SCHEMA)
            ])

    def upsert_habits_project_field_options(
            self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""
        inbox_big_plan_options = [{
            "color": self._get_stable_color(str(pl.notion_link_uuid)),
            "id": str(pl.notion_link_uuid),
            "value": format_name_for_option(pl.name)
        } for pl in project_labels]

        new_schema: JSONDictType = copy.deepcopy(self._SCHEMA)
        new_schema["project-name"]["options"] = inbox_big_plan_options  # type: ignore

        self._collections_manager.save_collection_no_merge(
            NotionLockKey(f"{self._KEY}:{ref_id}"), self._PAGE_NAME, self._PAGE_ICON, new_schema, "project-name")
        LOGGER.info("Updated the schema for the associated habit")

        new_view: JSONDictType = copy.deepcopy(NotionHabitsManager._DATABASE_BY_PROJECT_VIEW_SCHEMA)
        new_view["format"]["collection_groups"] = [{  # type: ignore
            "property": "project-name",
            "value": {
                "type": "select",
                "value": format_name_for_option(pl.name)
            },
            "hidden": False
        } for pl in sorted(project_labels, key=lambda x: x.created_time)] + [{
            "property": "project-name",
            "value": {"type": "select"},
            "hidden": True
        }]

        self._collections_manager.quick_update_view_for_collection(
            NotionLockKey(f"{self._KEY}:{ref_id}"), "database_by_project_view_id", new_view)
        LOGGER.info("Updated the projects view for the associated habits")

    def upsert_leaf(
            self, trunk_ref_id: EntityId, leaf: NotionHabit, extra_info: NotionInboxTaskCollection) -> NotionHabit:
        """Upsert a habit."""
        link = \
            self._collections_manager.upsert_collection_item(
                key=NotionLockKey(f"{leaf.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                new_row=leaf,
                copy_row_to_notion_row=lambda c, r, nr: self._copy_row_to_notion_row(c, r, nr, extra_info))
        return link.item_info

    def save_leaf(
            self, trunk_ref_id: EntityId, leaf: NotionHabit,
            extra_info: Optional[NotionInboxTaskCollection] = None) -> NotionHabit:
        """Update the Notion-side habit with new data."""
        try:
            link = \
                self._collections_manager.save_collection_item(
                    key=NotionLockKey(f"{leaf.ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                    row=leaf,
                    copy_row_to_notion_row=
                    lambda c, r, nr: self._copy_row_to_notion_row(c, r, nr, extra_info))
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionHabitNotFoundError(
                f"Notion habit with id {leaf.ref_id} could not be found") from err

    def load_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> NotionHabit:
        """Retrieve the Notion-side habit associated with a particular entity."""
        try:
            link = \
                self._collections_manager.load_collection_item(
                    key=NotionLockKey(f"{leaf_ref_id}"),
                    collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionHabitNotFoundError(
                f"Notion habit with id {leaf_ref_id} could not be found") from err

    def load_all_leaves(
            self, trunk_ref_id: EntityId) -> Iterable[NotionHabit]:
        """Retrieve all the Notion-side habits."""
        return [l.item_info for l in
                self._collections_manager.load_all_collection_items(
                    collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                    copy_notion_row_to_row=self._copy_notion_row_to_row)]

    def remove_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))
        except NotionCollectionItemNotFoundError as err:
            raise NotionHabitNotFoundError(
                f"Notion habit with id {leaf_ref_id} could not be found") from err

    def drop_all_leaves(self, trunk_ref_id: EntityId) -> None:
        """Remove all habits Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))

    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the habits tasks."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))

    def load_all_saved_notion_ids(
            self, trunk_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"))

    def link_local_and_notion_leaves(
            self, trunk_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionHabit, notion_row: CollectionRowBlock,
            inbox_collection_link: Optional[NotionInboxTaskCollection]) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        if row.ref_id is None:
            raise Exception(f"Habit row '{row.name}' which is synced must have a ref id")

        with client.with_transaction():
            notion_row.title = row.name
            notion_row.archived = row.archived
            notion_row.period = row.period
            notion_row.project_id = row.project_ref_id
            notion_row.project = row.project_name
            notion_row.eisenhower = row.eisen
            notion_row.difficulty = row.difficulty
            notion_row.actionable_from_day = row.actionable_from_day
            notion_row.actionable_from_month = row.actionable_from_month
            notion_row.due_at_time = row.due_at_time
            notion_row.due_at_day = row.due_at_day
            notion_row.due_at_month = row.due_at_month
            notion_row.skip_rule = row.skip_rule
            notion_row.repeats_in_period = row.repeats_in_period_count
            notion_row.suspended = row.suspended
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = str(row.ref_id) if row.ref_id else None

        if inbox_collection_link:
            LOGGER.info(f"Creating views structure for habit {notion_row}")

            client.attach_view_block_as_child_of_block(
                notion_row, 0, inbox_collection_link.notion_id,
                self._get_view_schema_for_habits_desc(row.ref_id))

        return notion_row

    def _copy_notion_row_to_row(self, habit_notion_row: CollectionRowBlock) -> NotionHabit:
        """Transform the live system data to something suitable for basic storage."""
        # pylint: disable=no-self-use
        return NotionHabit(
            notion_id=NotionId.from_raw(habit_notion_row.id),
            name=habit_notion_row.title,
            archived=habit_notion_row.archived,
            project_ref_id=habit_notion_row.project_id,
            project_name=habit_notion_row.project,
            period=habit_notion_row.period,
            eisen=habit_notion_row.eisenhower,
            difficulty=habit_notion_row.difficulty,
            actionable_from_day=habit_notion_row.actionable_from_day,
            actionable_from_month=habit_notion_row.actionable_from_month,
            due_at_time=habit_notion_row.due_at_time,
            due_at_day=habit_notion_row.due_at_day,
            due_at_month=habit_notion_row.due_at_month,
            skip_rule=habit_notion_row.skip_rule,
            repeats_in_period_count=habit_notion_row.repeats_in_period,
            suspended=habit_notion_row.suspended,
            last_edited_time=
            Timestamp.from_notion(habit_notion_row.last_edited_time),
            ref_id=EntityId.from_raw(habit_notion_row.ref_id) if habit_notion_row.ref_id else None)

    @staticmethod
    def _get_view_schema_for_habits_desc(habit_ref_id: EntityId) -> JSONDictType:
        """Get the view schema for a habit details view."""
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
                        "property": "habit-ref-id",
                        "filter": {
                            "operator": "string_is",
                            "value": {
                                "type": "exact",
                                "value": str(habit_ref_id)
                            }
                        }
                    }, {
                        "property": "source",
                        "filter": {
                            "operator": "enum_is",
                            "value": {
                                "type": "exact",
                                "value": InboxTaskSource.HABIT.for_notion()
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

    @staticmethod
    def _get_stable_color(option_id: str) -> str:
        """Return a random-ish yet stable color for a given name."""
        colors = [
            "gray",
            "brown",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "red"
        ]
        return colors[hashlib.sha256(option_id.encode("utf-8")).digest()[0] % len(colors)]
