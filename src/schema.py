"""Definitions for Notion-side schemas."""

import hashlib
import uuid

COLORS = [
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


def get_stable_color(option_id):
    """Return a random-ish yet stable color for a given name."""
    return COLORS[hashlib.sha256(option_id.encode("utf-8")).digest()[0] % len(COLORS)]


def format_name_for_option(option_name):
    """Nicely format the name of an option."""
    output = ""
    for char in option_name:
        if char.isalnum() or char == " ":
            output += char
    return output


def get_vacations_schema():
    """Get schemas for vacations screen."""
    vacations_schema = {
        "title": {
            "name": "Name",
            "type": "title"
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

    return vacations_schema


VACATIONS_DATABASE_VIEW_SCHEMA = {
    "name": "Database",
    "format": {
        "table_properties": [{
            "width": 300,
            "property": "title",
            "visible": True
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
        }]
    }
}

RECURRING_STATUS = "Recurring"
DONE_STATUS = "Done"
NOT_DONE_STATUS = "Not Done"
ARCHIVED_STATUS = "Archived"

INBOX_BIGPLAN_KEY = "bigplan2"

INBOX_TASK_ROW_DUE_DATE_KEY = "due_date"
INBOX_TASK_ROW_EISEN_KEY = "eisenhower"
INBOX_TASK_ROW_DIFFICULTY_KEY = "difficulty"
INBOX_TASK_ROW_FROM_SCRIPT_KEY = "from_script"
INBOX_TASK_ROW_PERIOD_KEY = "recurring_period"
INBOX_TASK_ROW_TIMELINE_KEY = "recurring_timeline"

RECURRING_TASKS_GROUP_KEY = "group"

BIG_PLAN_TASK_INBOX_ID_KEY = "inbox_id_ref"

INBOX_STATUS = {
    "Accepted": {
        "name": "Accepted",
        "color": "orange",
        "in_board": True
    },
    RECURRING_STATUS: {
        "name": RECURRING_STATUS,
        "color": "orange",
        "in_board": True
    },
    "In Progress": {
        "name": "In Progress",
        "color": "blue",
        "in_board": True
    },
    "Blocked": {
        "name": "Blocked",
        "color": "yellow",
        "in_board": True
    },
    "Not Done": {
        "name": "Not Done",
        "color": "red",
        "in_board": True
    },
    "Done": {
        "name": "Done",
        "color": "green",
        "in_board": True
    },
    "Archived": {
        "name": "Archived",
        "color": "gray",
        "in_board": False
    }
}

INBOX_EISENHOWER = {
    "Urgent": {
        "name": "Urgent",
        "color": "red"
    },
    "Important": {
        "name": "Important",
        "color": "blue"
    }
}

INBOX_DIFFICULTY = {
    "Easy": {
        "name": "Easy",
        "color": "blue"
    },
    "Medium": {
        "name": "Medium",
        "color": "green"
    },
    "Hard": {
        "name": "Hard",
        "color": "purple"
    }
}

INBOX_TIMELINE = {
    "Daily": {
        "name": "Daily",
        "color": "orange"
    },
    "Weekly": {
        "name": "Weekly",
        "color": "red"
    },
    "Monthly": {
        "name": "Monthly",
        "color": "blue"
    },
    "Quarterly": {
        "name": "Quarterly",
        "color": "green"
    },
    "Yearly": {
        "name": "Yearly",
        "color": "yellow"
    }
}

BIG_PLAN_STATUS = {
    "Accepted": {
        "name": "Accepted",
        "color": "orange",
        "in_board": True
    },
    "In Progress": {
        "name": "In Progress",
        "color": "blue",
        "in_board": True
    },
    "Blocked": {
        "name": "Blocked",
        "color": "yellow",
        "in_board": True
    },
    "Not Done": {
        "name": "Not Done",
        "color": "red",
        "in_board": True
    },
    "Done": {
        "name": "Done",
        "color": "green",
        "in_board": True
    },
    "Archived": {
        "name": "Archived",
        "color": "gray",
        "in_board": False
    }
}


def get_inbox_schema():
    """Get schemas for inbox screen."""
    inbox_schema = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "status": {
            "name": "Status",
            "type": "select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in INBOX_STATUS.values()]
        },
        INBOX_BIGPLAN_KEY: {
            "name": "Big Plan",
            "type": "select",
            "options": [{}]
        },
        "date": {
            "name": "Due Date",
            "type": "date"
        },
        "eisen": {
            "name": "Eisenhower",
            "type": "multi_select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in INBOX_EISENHOWER.values()]
        },
        "difficulty": {
            "name": "Difficulty",
            "type": "select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in INBOX_DIFFICULTY.values()]
        },
        "fromscript": {
            "name": "From Script",
            "type": "checkbox"
        },
        "period": {
            "name": "Recurring Period",
            "type": "select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in INBOX_TIMELINE.values()]
        },
        "timeline": {
            "name": "Recurring Timeline",
            "type": "text"
        }
    }

    return inbox_schema


INBOX_KANBAN_FORMAT = {
    "board_groups": [{
        "property": "status",
        "type": "select",
        "value": v["name"],
        "hidden": not v["in_board"]
    } for v in INBOX_STATUS.values()] + [{
        "property": "status",
        "type": "select",
        "hidden": True
    }],
    "board_groups2": [{
        "property": "status",
        "value": {
            "type": "select",
            "value": v["name"]
        },
        "hidden": not v["in_board"]
    } for v in INBOX_STATUS.values()] + [{
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
        "property": INBOX_BIGPLAN_KEY,
        "visible": True
    }, {
        "property": "date",
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
        "property": "period",
        "visible": True
    }, {
        "property": "timeline",
        "visible": False
    }],
    "board_cover_size": "small"
}

INBOX_KANBAN_ALL_VIEW_SCHEMA = {
    "name": "Kanban All",
    "query2": {
        "group_by": "status",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "date",
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
        }]
    },
    "format": INBOX_KANBAN_FORMAT
}

INBOX_KANBAN_URGENT_VIEW_SCHEMA = {
    "name": "Kanban Urgent",
    "query2": {
        "group_by": "status",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "date",
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
    "format": INBOX_KANBAN_FORMAT
}

INBOX_KANBAN_DUE_TODAY_VIEW_SCHEMA = {
    "name": "Kanban Due Today Or Exceeded",
    "query2": {
        "group_by": "status",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "date",
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
                "property": "date",
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
    "format": INBOX_KANBAN_FORMAT
}

INBOX_KANBAN_DUE_THIS_WEEK_VIEW_SCHEMA = {
    "name": "Kanban Due This Week Or Exceeded",
    "query2": {
        "group_by": "status",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "date",
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
                "property": "date",
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
    "format": INBOX_KANBAN_FORMAT
}

INBOX_KANBAN_DUE_THIS_MONTH_VIEW_SCHEMA = {
    "name": "Kanban Due This Month Or Exceeded.",
    "query2": {
        "group_by": "status",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "date",
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
                "property": "date",
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
    "format": INBOX_KANBAN_FORMAT
}

INBOX_CALENDAR_VIEW_SCHEMA = {
    "name": "Not Completed By Date",
    "query2": {
        "sort": [{
            "property": "date",
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
            "property": "status",
            "visible": True
        }, {
            "property": INBOX_BIGPLAN_KEY,
            "visible": True
        }, {
            "property": "date",
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

INBOX_DATABASE_VIEW_SCHEMA = {
    "name": "Database",
    "format": {
        "table_properties": [{
            "width": 300,
            "property": "title",
            "visible": True
        }, {
            "width": 100,
            "property": INBOX_BIGPLAN_KEY,
            "visible": True
        }, {
            "width": 100,
            "property": "status",
            "visible": True
        }, {
            "width": 100,
            "property": "date",
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


RECURRING_TASKS_PERIOD = {
    "Daily": {
        "name": "Daily",
        "color": "orange",
        "in_board": True
    },
    "Weekly": {
        "name": "Weekly",
        "color": "green",
        "in_board": True
    },
    "Monthly": {
        "name": "Monthly",
        "color": "yellow",
        "in_board": True
    },
    "Quarterly": {
        "name": "Quarterly",
        "color": "blue",
        "in_board": True
    },
    "Yearly": {
        "name": "Yearly",
        "color": "red",
        "in_board": True
    }
}


def get_recurring_tasks_schema():
    """Get schemas for the recurring tasks screen."""
    recurring_tasks_schema = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "period": {
            "name": "Period",
            "type": "select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in RECURRING_TASKS_PERIOD.values()]
        },
        RECURRING_TASKS_GROUP_KEY: {
            "name": "Group",
            "type": "select",
            "options": [{}]
        },
        "eisen": {
            "name": "Eisenhower",
            "type": "multi_select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in INBOX_EISENHOWER.values()]
        },
        "difficulty": {
            "name": "Difficulty",
            "type": "select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in INBOX_DIFFICULTY.values()]
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
        "must-do": {
            "name": "Must Do",
            "type": "checkbox"
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        }
    }

    return recurring_tasks_schema


RECURRING_TASKS_KANBAN_ALL_SCHEMA = {
    "name": "Kanban",
    "query2": {
        "group_by": "period",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "group",
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
        }]
    },
    "format": {
        "board_groups": [{
            "property": "period",
            "type": "select",
            "value": v["name"],
            "hidden": not v["in_board"]
        } for v in RECURRING_TASKS_PERIOD.values()],
        "board_groups2": [{
            "property": "period",
            "value": {
                "type": "select",
                "value": v["name"]
            },
            "hidden": not v["in_board"]
        } for v in RECURRING_TASKS_PERIOD.values()],
        "board_properties": [{
            "property": "period",
            "visible": False
        }, {
            "property": "group",
            "visible": True
        }, {
            "property": "eisen",
            "visible": True
        }, {
            "property": "difficulty",
            "visible": True
        }, {
            "property": "must-do",
            "visible": False
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
            "property": "ref-id",
            "visible": False
        }],
        "board_cover_size": "small"
    }
}


RECURRING_TASKS_DATABASE_VIEW_SCHEMA = {
    "name": "Database",
    "format": {
        "table_properties": [{
            "width": 300,
            "property": "title",
            "visible": True
        }, {
            "width": 100,
            "property": "period",
            "visible": True
        }, {
            "width": 100,
            "property": RECURRING_TASKS_PERIOD,
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
            "property": "must-do",
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
            "property": "ref-id",
            "visible": False
        }]
    }
}


def get_big_plan_schema():
    """Get schemas for big plan screen."""
    big_plan_schema = {
        "title": {
            "name": "Name",
            "type": "title"
        },
        "status": {
            "name": "Status",
            "type": "select",
            "options": [{
                "color": v["color"],
                "id": str(uuid.uuid4()),
                "value": v["name"]
            } for v in BIG_PLAN_STATUS.values()]
        },
        "date": {
            "name": "Due Date",
            "type": "date"
        },
        "inboxid": {
            "name": "Inbox Id Ref",
            "type": "text"
        }
    }

    return big_plan_schema


BIG_PLAN_FORMAT = {
    "board_groups": [{
        "property": "status",
        "type": "select",
        "value": v["name"],
        "hidden": not v["in_board"]
    } for v in BIG_PLAN_STATUS.values()] + [{
        "property": "status",
        "type": "select",
        "hidden": True
    }],
    "board_groups2": [{
        "property": "status",
        "value": {
            "type": "select",
            "value": v["name"]
        },
        "hidden": not v["in_board"]
    } for v in INBOX_STATUS.values()] + [{
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
        "property": "date",
        "visible": True
    }],
    "board_cover_size": "small"
}


BIG_PLAN_KANBAN_ALL_SCHEMA = {
    "name": "Kanban All",
    "query2": {
        "group_by": "status",
        "filter_operator": "and",
        "aggregations": [{
            "aggregator": "count"
        }],
        "sort": [{
            "property": "date",
            "direction": "ascending"
        }]
    },
    "format": BIG_PLAN_FORMAT
}


BIG_PLAN_DATABASE_VIEW_SCHEMA = {
    "name": "Database",
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
            "property": "date",
            "visible": True
        }, {
            "width": 100,
            "property": "inboxid",
            "visible": False
        }]
    }
}


def get_view_schema_for_big_plan_desc(big_plan_name):
    """Get the view schema for a big plan details view."""
    big_plan_view_schema = {
        "name": "Inbox Tasks",
        "query2": {
            "filter_operator": "and",
            "sort": [{
                "property": "status",
                "direction": "ascending"
            }, {
                "property": "date",
                "direction": "ascending"
            }],
            "filter": {
                "operator": "and",
                "filters": [{
                    "property": INBOX_BIGPLAN_KEY,
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
                "property": INBOX_BIGPLAN_KEY,
                "visible": False
            }, {
                "width": 100,
                "property": "date",
                "visible": True
            }, {
                "width": 100,
                "property": "eisen",
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

    return big_plan_view_schema
