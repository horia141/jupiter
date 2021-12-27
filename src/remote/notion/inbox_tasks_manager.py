"""The centralised point for interacting with Notion inbox tasks."""
import copy
import hashlib
import logging
import uuid
from typing import Final, ClassVar, cast, Dict, Optional, Iterable

from notion.collection import CollectionRowBlock

from domain.adate import ADate
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, InboxTaskBigPlanLabel, \
    NotionInboxTaskCollectionNotFoundError, NotionInboxTaskNotFoundError
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from domain.projects.notion_project import NotionProject
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_type import RecurringTaskType
from framework.base.entity_id import EntityId
from framework.base.notion_id import NotionId
from framework.base.timestamp import Timestamp
from framework.json import JSONDictType
from remote.notion.common import NotionLockKey, NotionPageLink, format_name_for_option, \
    clean_eisenhower
from remote.notion.infra.client import NotionClient, NotionFieldProps, NotionFieldShow
from remote.notion.infra.collections_manager import CollectionsManager, NotionCollectionNotFoundError, \
    NotionCollectionItemNotFoundError
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionInboxTasksManager(InboxTaskNotionManager):
    """The centralised point for interacting with Notion inbox tasks."""

    _KEY: ClassVar[str] = "inbox-tasks"

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

    _SOURCE: ClassVar[JSONDictType] = {
        "User": {
            "name": InboxTaskSource.USER.for_notion(),
            "color": "blue"
        },
        "Big Plan": {
            "name": InboxTaskSource.BIG_PLAN.for_notion(),
            "color": "green"
        },
        "Recurring Task": {
            "name": InboxTaskSource.RECURRING_TASK.for_notion(),
            "color": "yellow"
        },
        "Metric": {
            "name": InboxTaskSource.METRIC.for_notion(),
            "color": "red"
        },
        "Person Catchup": {
            "name": InboxTaskSource.PERSON_CATCH_UP.for_notion(),
            "color": "purple"
        },
        "Person Birthday": {
            "name": InboxTaskSource.PERSON_BIRTHDAY.for_notion(),
            "color": "orange"
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

    _RECURRING_TASK_PERIOD: ClassVar[JSONDictType] = {
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

    _RECURRING_TASK_TYPE: ClassVar[JSONDictType] = {
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
        "source": {
            "name": "Source",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _SOURCE.values()]
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
        "metric-ref-id": {
            "name": "Metric Id",
            "type": "text"
        },
        "person-ref-id": {
            "name": "Person Id",
            "type": "text"
        },
        "actionable-date": {
            "name": "Actionable Date",
            "type": "date"
        },
        "due-date": {
            "name": "Due Date",
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
        "timeline": {
            "name": "Recurring Timeline",
            "type": "text"
        },
        "period": {
            "name": "Recurring Period",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _RECURRING_TASK_PERIOD.values()]
        },
        "recurring-task-type": {
            "name": "Recurring Type",
            "type": "select",
            "options": [{
                "color": cast(Dict[str, str], v)["color"],
                "id": str(uuid.uuid4()),
                "value": cast(Dict[str, str], v)["name"]
            } for v in _RECURRING_TASK_TYPE.values()]
        },
        "recurring-task-gen-right-now": {
            "name": "Recurring Gen Right Now",
            "type": "date"
        },
        "last-edited-time": {
            "name": "Last Edited Time",
            "type": "last_edited_time"
        },
    }

    _SCHEMA_PROPERTIES = [
        NotionFieldProps(name="title", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="status", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="source", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="eisen", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="difficulty", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="actionable-date", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="due-date", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="archived", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="ref-id", show=NotionFieldShow.SHOW),
        NotionFieldProps(name="big-plan-ref-id", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="bigplan2", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="recurring-task-ref-id", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="recurring-task-type", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="metric-ref-id", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="person-ref-id", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="period", show=NotionFieldShow.HIDE_IF_EMPTY),
        NotionFieldProps(name="fromscript", show=NotionFieldShow.HIDE),
        NotionFieldProps(name="timeline", show=NotionFieldShow.HIDE),
        NotionFieldProps(name="recurring-task-gen-right-now", show=NotionFieldShow.HIDE),
        NotionFieldProps(name="last-edited-time", show=NotionFieldShow.HIDE)
    ]

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
            "property": "source",
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
            "property": "metric-ref-id",
            "visible": False
        }, {
            "property": "person-ref-id",
            "visible": False
        }, {
            "property": "actionable-date",
            "visible": True
        }, {
            "property": "due-date",
            "visible": True
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
            "property": "timeline",
            "visible": False
        }, {
            "property": "period",
            "visible": True
        }, {
            "property": "recurring-task-type",
            "visible": True
        }, {
            "property": "recurring-task-gen-right-now",
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
                    "operator": "or",
                    "filters": [{
                        "property": "actionable-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "today"
                            }
                        }
                    }, {
                        "property": "actionable-date",
                        "filter": {
                            "operator": "is_empty"
                        }
                    }]
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
                    "operator": "or",
                    "filters": [{
                        "property": "actionable-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "today"
                            }
                        }
                    }, {
                        "property": "actionable-date",
                        "filter": {
                            "operator": "today"
                        }
                    }]
                }, {
                    "operator": "or",
                    "filters": [{
                        "property": "due-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "tomorrow"
                            }
                        }
                    }, {
                        "property": "due-date",
                        "filter": {
                            "operator": "is_empty"
                        }
                    }]
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
                    "operator": "or",
                    "filters": [{
                        "property": "actionable-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "today"
                            }
                        }
                    }, {
                        "property": "actionable-date",
                        "filter": {
                            "operator": "is_empty"
                        }
                    }]
                }, {
                    "operator": "or",
                    "filters": [{
                        "property": "due-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "one_week_from_now"
                            }
                        }
                    }, {
                        "property": "due-date",
                        "filter": {
                            "operator": "is_empty"
                        }
                    }]
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
                    "operator": "or",
                    "filters": [{
                        "property": "actionable-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "today"
                            }
                        }
                    }, {
                        "property": "actionable-date",
                        "filter": {
                            "operator": "is_empty"
                        }
                    }]
                }, {
                    "operator": "or",
                    "filters": [{
                        "property": "due-date",
                        "filter": {
                            "operator": "date_is_on_or_before",
                            "value": {
                                "type": "relative",
                                "value": "one_month_from_now"
                            }
                        }
                    }, {
                        "property": "due-date",
                        "filter": {
                            "operator": "is_empty"
                        }
                    }]
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
                "property": "source",
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
                "property": "metric-ref-id",
                "visible": False
            }, {
                "property": "person-ref-id",
                "visible": False
            }, {
                "property": "actionable-date",
                "visible": False
            }, {
                "property": "due-date",
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
                "property": "timeline",
                "visible": False
            }, {
                "property": "period",
                "visible": True
            }, {
                "property": "recurring-task-type",
                "visible": True
            }, {
                "property": "recurring-task-gen-right-now",
                "visible": False
            }, {
                "property": "last-edited-time",
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
                "visible": True
            }, {
                "width": 100,
                "property": "big-plan-ref-id",
                "visible": True
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
                "property": "metric-ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "person-ref-id",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }, {
                "width": 100,
                "property": "status",
                "visible": True
            }, {
                "width": 100,
                "property": "source",
                "visible": True
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
                "visible": True
            }, {
                "width": 100,
                "property": "timeline",
                "visible": True
            }, {
                "width": 100,
                "property": "period",
                "visible": True
            }, {
                "width": 100,
                "property": "recurring-task-type",
                "visible": True
            }, {
                "width": 100,
                "property": "recurring-task-gen-right-now",
                "visible": True
            }, {
                "width": 100,
                "property": "archived",
                "visible": True
            }, {
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

    def upsert_inbox_task_collection(
            self, notion_project: NotionProject,
            inbox_task_collection: NotionInboxTaskCollection) -> NotionInboxTaskCollection:
        """Upsert the Notion-side inbox task."""
        collection_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{inbox_task_collection.ref_id}"),
            parent_page=NotionPageLink(notion_project.notion_id),
            name=self._PAGE_NAME,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "kanban_all_view_id": NotionInboxTasksManager._KANBAN_ALL_VIEW_SCHEMA,
                "kanban_urgent_view_id": NotionInboxTasksManager._KANBAN_URGENT_VIEW_SCHEMA,
                "kanban_due_today_view_id": NotionInboxTasksManager._KANBAN_DUE_TODAY_VIEW_SCHEMA,
                "kanban_due_this_week_view_id": NotionInboxTasksManager._KANBAN_DUE_THIS_WEEK_VIEW_SCHEMA,
                "kanban_due_this_month_view_id": NotionInboxTasksManager._KANBAN_DUE_THIS_MONTH_VIEW_SCHEMA,
                "calendar_view_id": NotionInboxTasksManager._CALENDAR_VIEW_SCHEMA,
                "database_view_id": NotionInboxTasksManager._DATABASE_VIEW_SCHEMA
            })

        return NotionInboxTaskCollection(
            notion_id=collection_link.collection_id,
            ref_id=inbox_task_collection.ref_id)

    def load_inbox_task_collection(self, ref_id: EntityId) -> NotionInboxTaskCollection:
        """Get the Notion collection for this inbox task collection."""
        try:
            return NotionInboxTaskCollection(
                ref_id=ref_id,
                notion_id=self._collections_manager.load_collection(
                    NotionLockKey(f"{self._KEY}:{ref_id}")).collection_id)
        except NotionCollectionNotFoundError as err:
            raise NotionInboxTaskCollectionNotFoundError(
                f"Notion inbox task collection with id {ref_id} was not found") from err

    def remove_inbox_tasks_collection(self, ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""
        try:
            return self._collections_manager.remove_collection(
                NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionInboxTaskCollectionNotFoundError(
                f"Notion inbox task collection with id {ref_id} was not found") from err

    def upsert_inbox_tasks_big_plan_field_options(
            self, ref_id: EntityId, big_plans_labels: Iterable[InboxTaskBigPlanLabel]) -> None:
        """Upsert the Notion-side structure for the 'big plan' select field."""
        inbox_big_plan_options = [{
            "color": self._get_stable_color(str(bp.notion_link_uuid)),
            "id": str(bp.notion_link_uuid),
            "value": format_name_for_option(bp.name)
        } for bp in big_plans_labels]

        new_schema: JSONDictType = copy.deepcopy(self._SCHEMA)
        new_schema["bigplan2"]["options"] = inbox_big_plan_options  # type: ignore

        self._collections_manager.save_collection_no_merge(
            NotionLockKey(f"{self._KEY}:{ref_id}"), self._PAGE_NAME, new_schema)
        LOGGER.info("Updated the schema for the associated inbox")

    def upsert_inbox_task(
            self, inbox_task_collection_ref_id: EntityId, inbox_task: NotionInboxTask) -> NotionInboxTask:
        """Upsert a inbox task."""
        return self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{inbox_task.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"),
            new_row=inbox_task,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def save_inbox_task(self, inbox_task_collection_ref_id: EntityId, inbox_task: NotionInboxTask) -> NotionInboxTask:
        """Update the Notion-side inbox task with new data."""
        try:
            return self._collections_manager.save_collection_item(
                key=NotionLockKey(f"{inbox_task.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"),
                row=inbox_task,
                copy_row_to_notion_row=self._copy_row_to_notion_row)
        except NotionCollectionItemNotFoundError as err:
            raise NotionInboxTaskNotFoundError(
                f"Notion inbox task with id {inbox_task.ref_id} was not found") from err

    def load_all_inbox_tasks(self, inbox_task_collection_ref_id: EntityId) -> Iterable[NotionInboxTask]:
        """Retrieve all the Notion-side inbox tasks."""
        return self._collections_manager.load_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def load_inbox_task(self, inbox_task_collection_ref_id: EntityId, ref_id: EntityId) -> NotionInboxTask:
        """Retrieve the Notion-side inbox task associated with a particular entity."""
        try:
            return self._collections_manager.load_collection_item(
                key=NotionLockKey(f"{ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"),
                copy_notion_row_to_row=self._copy_notion_row_to_row)
        except NotionCollectionItemNotFoundError as err:
            raise NotionInboxTaskNotFoundError(
                f"Notion inbox task with id {ref_id} was not found") from err

    def remove_inbox_task(self, inbox_task_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        self._collections_manager.remove_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"))

    def drop_all_inbox_tasks(self, inbox_task_collection_ref_id: EntityId) -> None:
        """Remove all inbox tasks Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"))

    def link_local_and_notion_inbox_task(
            self, inbox_task_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def load_all_saved_inbox_tasks_notion_ids(self, inbox_task_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"))

    def load_all_saved_inbox_tasks_ref_ids(self, inbox_task_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the inbox tasks tasks."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{inbox_task_collection_ref_id}"))

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionInboxTask, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.title = row.name
            notion_row.source = row.source
            notion_row.archived = row.archived
            notion_row.big_plan_id = row.big_plan_ref_id
            if row.big_plan_name:
                notion_row.big_plan = row.big_plan_name
            notion_row.recurring_task_id = row.recurring_task_ref_id
            notion_row.metric_id = row.metric_ref_id
            notion_row.person_id = row.person_ref_id
            notion_row.status = row.status
            notion_row.eisenhower = row.eisen
            notion_row.difficulty = row.difficulty
            notion_row.actionable_date = \
                row.actionable_date.to_notion(self._global_properties.timezone) if row.actionable_date else None
            notion_row.due_date = row.due_date.to_notion(self._global_properties.timezone) if row.due_date else None
            notion_row.from_script = row.from_script
            notion_row.recurring_timeline = row.recurring_timeline
            notion_row.recurring_period = row.recurring_period
            notion_row.recurring_type = row.recurring_type
            notion_row.recurring_gen_right_now = \
                row.recurring_gen_right_now.to_notion(self._global_properties.timezone) \
                if row.recurring_gen_right_now else None
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = row.ref_id

        return notion_row

    def _copy_notion_row_to_row(self, inbox_task_notion_row: CollectionRowBlock) -> NotionInboxTask:
        """Transform the live system data to something suitable for basic storage."""
        return NotionInboxTask(
            notion_id=NotionId.from_raw(inbox_task_notion_row.id),
            source=inbox_task_notion_row.source,
            name=inbox_task_notion_row.title,
            archived=inbox_task_notion_row.archived,
            big_plan_ref_id=inbox_task_notion_row.big_plan_id,
            big_plan_name=inbox_task_notion_row.big_plan,
            recurring_task_ref_id=inbox_task_notion_row.recurring_task_id,
            metric_ref_id=inbox_task_notion_row.metric_id,
            person_ref_id=inbox_task_notion_row.person_id,
            status=inbox_task_notion_row.status,
            eisen=clean_eisenhower(inbox_task_notion_row.eisenhower),
            difficulty=inbox_task_notion_row.difficulty,
            actionable_date=ADate.from_notion(self._global_properties.timezone, inbox_task_notion_row.actionable_date)
            if inbox_task_notion_row.actionable_date else None,
            due_date=ADate.from_notion(self._global_properties.timezone, inbox_task_notion_row.due_date)
            if inbox_task_notion_row.due_date else None,
            from_script=inbox_task_notion_row.from_script,
            recurring_timeline=inbox_task_notion_row.recurring_timeline,
            recurring_period=inbox_task_notion_row.recurring_period,
            recurring_type=inbox_task_notion_row.recurring_type,
            recurring_gen_right_now=
            ADate.from_notion(self._global_properties.timezone, inbox_task_notion_row.recurring_gen_right_now)
            if inbox_task_notion_row.recurring_gen_right_now else None,
            last_edited_time=
            Timestamp.from_notion(inbox_task_notion_row.last_edited_time),
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
