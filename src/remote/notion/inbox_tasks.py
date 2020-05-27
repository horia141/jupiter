"""The collection for inbox tasks."""
import copy
import hashlib
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
import typing
from typing import Final, Optional, Dict, ClassVar, Iterable, List, cast

import pendulum
from notion.collection import CollectionRowBlock


from models.basic import EntityId, InboxTaskStatus, Eisen, Difficulty, RecurringTaskPeriod
from remote.notion import common
from remote.notion.client import NotionClient
from remote.notion.collection import NotionCollection, BasicRowType, NotionCollectionKWArgsType
from remote.notion.common import NotionId, NotionPageLink, NotionCollectionLink, format_name_for_option
from remote.notion.connection import NotionConnection
from repository.big_plans import BigPlan
from utils.storage import JSONDictType

LOGGER = logging.getLogger(__name__)


@dataclass()
class InboxTaskRow(BasicRowType):
    """An inbox task on Notion side."""

    name: str
    archived: bool
    created_date: Optional[pendulum.DateTime]
    big_plan_ref_id: Optional[str]
    big_plan_name: Optional[str]
    recurring_task_ref_id: Optional[str]
    status: Optional[str]
    eisen: Optional[List[str]]
    difficulty: Optional[str]
    due_date: Optional[pendulum.DateTime]
    from_script: bool
    recurring_period: Optional[str]
    recurring_timeline: Optional[str]


class InboxTasksCollection:
    """A collection on Notion side for inbox tasks."""

    _LOCK_FILE_PATH: ClassVar[Path] = Path("/data/inbox-tasks.lock.yaml")

    _PAGE_NAME: ClassVar[str] = "Inbox Tasks"
    _STATUS: ClassVar[JSONDictType] = {
        "Not Started": {
            "name": InboxTaskStatus.NOT_STARTED.for_notion(),
            "color": "gray",
            "in_board": False
        },
        "Accepted": {
            "name": InboxTaskStatus.ACCEPTED.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "Recurring": {
            "name": InboxTaskStatus.RECURRING.for_notion(),
            "color": "orange",
            "in_board": True
        },
        "In Progress": {
            "name": InboxTaskStatus.IN_PROGRESS.for_notion(),
            "color": "blue",
            "in_board": True
        },
        "Blocked": {
            "name": InboxTaskStatus.BLOCKED.for_notion(),
            "color": "yellow",
            "in_board": True
        },
        "Not Done": {
            "name": InboxTaskStatus.NOT_DONE.for_notion(),
            "color": "red",
            "in_board": True
        },
        "Done": {
            "name": InboxTaskStatus.DONE.for_notion(),
            "color": "green",
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

    _TASK_PERIOD: ClassVar[JSONDictType] = {
        "Daily": {
            "name": RecurringTaskPeriod.DAILY.for_notion(),
            "color": "orange"
        },
        "Weekly": {
            "name": RecurringTaskPeriod.WEEKLY.for_notion(),
            "color": "red"
        },
        "Monthly": {
            "name": RecurringTaskPeriod.MONTHLY.for_notion(),
            "color": "blue"
        },
        "Quarterly": {
            "name": RecurringTaskPeriod.QUARTERLY.for_notion(),
            "color": "green"
        },
        "Yearly": {
            "name": RecurringTaskPeriod.YEARLY.for_notion(),
            "color": "yellow"
        }
    }

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
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
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "big-plan-ref-id": {
            "name": "Big Plan Id",
            "type": "text"
        },
        "bigplan2": {
            "name": "Big Plan",
            "type": "select",
            "options": [{"color": "gray", "id": str(uuid.uuid4()), "value": "None"}]
        },
        "recurring-task-ref-id": {
            "name": "Recurring Task Id",
            "type": "text"
        },
        "due-date": {
            "name": "Due Date",
            "type": "date"
        },
        "created-date": {
            "name": "Created Date",
            "type": "date"
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
        "fromscript": {
            "name": "From Script",
            "type": "checkbox"
        },
        "period": {
            "name": "Recurring Period",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _TASK_PERIOD.values()]
        },
        "timeline": {
            "name": "Recurring Timeline",
            "type": "text"
        }
    }

    _KANBAN_FORMAT: ClassVar[JSONDictType] = {
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
            "property": "ref-id",
            "visible": False
        }, {
            "property": "status",
            "visible": False
        }, {
            "property": "archived",
            "visible": False
        }, {
            "property": "big-plan-ref-id",
            "visible": False
        }, {
            "property": "bigplan2",
            "visible": True
        }, {
            "property": "recurring-task-ref-id",
            "visible": False
        }, {
            "property": "due-date",
            "visible": True
        }, {
            "property": "created-date",
            "visible": False
        }, {
            "property": "eisen",
            "visible": True
        }, {
            "property": "difficulty",
            "visible": True
        }, {
            "property": "fromscript",
            "visible": False
        }, {
            "property": "period",
            "visible": True
        }, {
            "property": "timeline",
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
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "fromscript",
                "direction": "ascending"
            }, {
                "property": "period",
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
        "format": _KANBAN_FORMAT
    }

    _KANBAN_URGENT_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban Urgent",
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
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "fromscript",
                "direction": "ascending"
            }, {
                "property": "period",
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
                }, {
                    "property": "status",
                    "filter": {
                        "operator": "enum_is_not",
                        "value": {
                            "type": "exact",
                            "value": "Done"
                        }
                    }
                }, {
                    "property": "status",
                    "filter": {
                        "operator": "enum_is_not",
                        "value": {
                            "type": "exact",
                            "value": "Not Done"
                        }
                    }
                }, {
                    "property": "eisen",
                    "filter": {
                        "operator": "enum_contains",
                        "value": {
                            "type": "exact",
                            "value": "Urgent"
                        }
                    }
                }]
            }
        },
        "format": _KANBAN_FORMAT
    }

    _KANBAN_DUE_TODAY_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban Due Today Or Exceeded",
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
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "fromscript",
                "direction": "ascending"
            }, {
                "property": "period",
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
                }, {
                    "property": "due-date",
                    "filter": {
                        "operator": "date_is_on_or_before",
                        "value": {
                            "type": "relative",
                            "value": "tomorrow"
                        }
                    }
                }]
            }
        },
        "format": _KANBAN_FORMAT
    }

    _KANBAN_DUE_THIS_WEEK_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban Due This Week Or Exceeded",
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
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "fromscript",
                "direction": "ascending"
            }, {
                "property": "period",
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
                }, {
                    "property": "due-date",
                    "filter": {
                        "operator": "date_is_on_or_before",
                        "value": {
                            "type": "relative",
                            "value": "one_week_from_now"
                        }
                    }
                }]
            }
        },
        "format": _KANBAN_FORMAT
    }

    _KANBAN_DUE_THIS_MONTH_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban Due This Month Or Exceeded",
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
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "fromscript",
                "direction": "ascending"
            }, {
                "property": "period",
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
                }, {
                    "property": "due-date",
                    "filter": {
                        "operator": "date_is_on_or_before",
                        "value": {
                            "type": "relative",
                            "value": "one_month_from_now"
                        }
                    }
                }]
            }
        },
        "format": _KANBAN_FORMAT
    }

    _CALENDAR_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Not Completed By Date",
        "type": "calendar",
        "query2": {
            "sort": [{
                "property": "due-date",
                "direction": "ascending"
            }, {
                "property": "eisen",
                "direction": "ascending"
            }, {
                "property": "difficulty",
                "direction": "ascending"
            }, {
                "property": "fromscript",
                "direction": "ascending"
            }, {
                "property": "period",
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
                }, {
                    "property": "status",
                    "filter": {
                        "operator": "enum_is_not",
                        "value": {
                            "type": "exact",
                            "value": "Done"
                        }
                    }
                }]
            }
        },
        "format": {
            "calendar_properties": [{
                "property": "title",
                "visible": True
            }, {
                "property": "ref-id",
                "visible": False,
            }, {
                "property": "status",
                "visible": True
            }, {
                "property": "archived",
                "visible": False
            }, {
                "property": "big-plan-ref-id",
                "visible": False
            }, {
                "property": "bigplan2",
                "visible": True
            }, {
                "property": "recurring-task-ref-id",
                "visible": False
            }, {
                "property": "due-date",
                "visible": False
            }, {
                "property": "created-date",
                "visible": False
            }, {
                "property": "eisen",
                "visible": True
            }, {
                "property": "difficulty",
                "visible": True
            }, {
                "property": "fromscript",
                "visible": False
            }, {
                "property": "period",
                "visible": True
            }, {
                "property": "timeline",
                "visible": False
            }]
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
                "property": "ref-id",
                "visible": False
            }, {
                "width": 100,
                "property": "big-plan-ref-id",
                "visible": False
            }, {
                "width": 100,
                "property": "bigplan2",
                "visible": True
            }, {
                "width": 100,
                "property": "recurring-task-ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
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
                "property": "created-date",
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
                "visible": True
            }, {
                "width": 100,
                "property": "period",
                "visible": True
            }, {
                "width": 100,
                "property": "timeline",
                "visible": True
            }]
        }
    }

    _collection: Final[NotionCollection[InboxTaskRow]]

    def __init__(self, connection: NotionConnection) -> None:
        """Constructor."""
        self._collection = NotionCollection[InboxTaskRow](connection, self._LOCK_FILE_PATH, self)

    def __enter__(self) -> 'InboxTasksCollection':
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

    def upsert_inbox_tasks_structure(
            self, project_ref_id: EntityId, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Upsert the Notion-side structure for this collection."""
        return self._collection.upsert_structure(project_ref_id, parent_page)

    def remove_inbox_tasks_structure(self, project_ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""
        return self._collection.remove_structure(project_ref_id)

    def get_inbox_tasks_structure(self, project_ref_id: EntityId) -> NotionCollectionLink:
        """Retrieve the Notion-side structure link for this collection."""
        return self._collection.get_structure(project_ref_id)

    def upsert_inbox_tasks_big_plan_field_options(
            self, project_ref_id: EntityId, big_plans: Iterable[BigPlan]) -> None:
        """Upsert the Notion-side structure for the 'big plan' select field."""
        inbox_big_plan_options = [{
            "color": self._get_stable_color(str(bp.notion_link_uuid)),
            "id": str(bp.notion_link_uuid),
            "value": format_name_for_option(bp.name)
        } for bp in big_plans]

        new_schema: JSONDictType = copy.deepcopy(self._SCHEMA)
        new_schema["bigplan2"]["options"] = inbox_big_plan_options  # type: ignore

        self._collection.update_schema(project_ref_id, new_schema)
        LOGGER.info("Updated the schema for the associated inbox")

    def create_inbox_task(
            self, project_ref_id: EntityId, name: str, big_plan_ref_id: Optional[EntityId],
            big_plan_name: Optional[str], recurring_task_ref_id: Optional[EntityId], status: str,
            eisen: Optional[List[str]], difficulty: Optional[str], due_date: Optional[pendulum.DateTime],
            recurring_period: Optional[str], recurring_timeline: Optional[str], ref_id: EntityId) -> InboxTaskRow:
        """Create an inbox task."""
        new_inbox_task_row = InboxTaskRow(
            notion_id=NotionId("FAKE-FAKE-FAKE"),
            name=name,
            archived=False,
            created_date=pendulum.now(),
            big_plan_ref_id=big_plan_ref_id,
            big_plan_name=big_plan_name,
            recurring_task_ref_id=recurring_task_ref_id,
            status=status,
            eisen=eisen,
            difficulty=difficulty,
            due_date=due_date,
            from_script=True,
            recurring_period=recurring_period,
            recurring_timeline=recurring_timeline,
            ref_id=ref_id)
        return cast(InboxTaskRow, self._collection.create(project_ref_id, new_inbox_task_row))

    def link_local_and_notion_entries(self, project_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notio none, useful in syncing processes."""
        self._collection.link_local_and_notion_entries(project_ref_id, ref_id, notion_id)

    def archive_inbox_task(self, project_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a particular inbox task."""
        self._collection.archive(project_ref_id, ref_id)

    def load_all_inbox_tasks(self, project_ref_id: EntityId) -> Iterable[InboxTaskRow]:
        """Retrieve all the Notion-side inbox tasks."""
        return cast(Iterable[InboxTaskRow], self._collection.load_all(project_ref_id))

    def load_inbox_task(self, project_ref_id: EntityId, ref_id: EntityId) -> InboxTaskRow:
        """Retrieve the Notion-side inbox task associated with a particular entity."""
        return cast(InboxTaskRow, self._collection.load(project_ref_id, ref_id))

    def save_inbox_task(self, project_ref_id: EntityId, new_inbox_task_row: InboxTaskRow) -> None:
        """Update the Notion-side inbox task with new data."""
        self._collection.save(project_ref_id, new_inbox_task_row)

    def hard_remove_inbox_task(self, project_ref_id: EntityId, ref_id: EntityId) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        self._collection.hard_remove(project_ref_id, ref_id)

    @staticmethod
    def get_page_name() -> str:
        """Get the name for the page."""
        return InboxTasksCollection._PAGE_NAME

    @staticmethod
    def get_notion_schema() -> JSONDictType:
        """Get the Notion schema for the collection."""
        return InboxTasksCollection._SCHEMA

    @staticmethod
    def get_view_schemas() -> Dict[str, JSONDictType]:
        """Get the Notion view schemas for the collection."""
        return {
            "kanban_all_view_id": InboxTasksCollection._KANBAN_ALL_VIEW_SCHEMA,
            "kanban_urgent_view_id": InboxTasksCollection._KANBAN_URGENT_VIEW_SCHEMA,
            "kanban_due_today_view_id": InboxTasksCollection._KANBAN_DUE_TODAY_VIEW_SCHEMA,
            "kanban_due_this_week_view_id": InboxTasksCollection._KANBAN_DUE_THIS_WEEK_VIEW_SCHEMA,
            "kanban_due_this_month_view_id": InboxTasksCollection._KANBAN_DUE_THIS_MONTH_VIEW_SCHEMA,
            "calendar_view_id": InboxTasksCollection._CALENDAR_VIEW_SCHEMA,
            "database_view_id": InboxTasksCollection._DATABASE_VIEW_SCHEMA
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
        # As another special case, the recurring tasks group key is left to whatever value it had
        # before since this thing is managed by the other flows!
        for (schema_item_name, schema_item) in new_schema.items():
            if schema_item_name in ("bigplan2", "group"):
                combined_schema[schema_item_name] = old_schema[schema_item_name] \
                    if (schema_item_name in old_schema and old_schema[schema_item_name]["type"] == "select") \
                    else schema_item
            elif schema_item["type"] == "select" or schema_item["type"] == "multi_select":
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
            client: NotionClient, row: InboxTaskRow, notion_row: CollectionRowBlock,
            **kwargs: NotionCollectionKWArgsType) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        # pylint: disable=unused-argument
        notion_row.title = row.name
        notion_row.archived = row.archived
        notion_row.created_date = row.created_date
        notion_row.big_plan_id = row.big_plan_ref_id
        if row.big_plan_name:
            notion_row.big_plan = row.big_plan_name
        notion_row.recurring_task_id = row.recurring_task_ref_id
        notion_row.status = row.status
        notion_row.eisenhower = row.eisen
        notion_row.difficulty = row.difficulty
        notion_row.due_date = row.due_date
        notion_row.from_script = row.from_script
        notion_row.recurring_period = row.recurring_period
        notion_row.recurring_timeline = row.recurring_timeline
        notion_row.ref_id = row.ref_id

        return notion_row

    @staticmethod
    def copy_notion_row_to_row(inbox_task_notion_row: CollectionRowBlock) -> InboxTaskRow:
        """Transform the live system data to something suitable for basic storage."""
        return InboxTaskRow(
            notion_id=inbox_task_notion_row.id,
            name=inbox_task_notion_row.title,
            archived=inbox_task_notion_row.archived,
            created_date=pendulum.parse(str(inbox_task_notion_row.created_date.start))
            if inbox_task_notion_row.created_date else None,
            big_plan_ref_id=inbox_task_notion_row.big_plan_id,
            big_plan_name=inbox_task_notion_row.big_plan,
            recurring_task_ref_id=inbox_task_notion_row.recurring_task_id,
            status=inbox_task_notion_row.status,
            eisen=common.clean_eisenhower(inbox_task_notion_row.eisenhower),
            difficulty=inbox_task_notion_row.difficulty,
            due_date=pendulum.parse(str(inbox_task_notion_row.due_date.start))
            if inbox_task_notion_row.due_date else None,
            from_script=inbox_task_notion_row.from_script,
            recurring_period=inbox_task_notion_row.recurring_period,
            recurring_timeline=inbox_task_notion_row.recurring_timeline,
            ref_id=inbox_task_notion_row.ref_id)

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
