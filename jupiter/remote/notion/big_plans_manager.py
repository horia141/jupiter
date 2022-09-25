"""The centralised point for interacting with Notion big plans."""
import copy
import hashlib
import uuid
from typing import Final, ClassVar, cast, Dict, Optional, Iterable

from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_notion_manager import (
    BigPlanNotionManager,
    NotionBigPlanNotFoundError,
)
from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey, format_name_for_option
from jupiter.remote.notion.infra.client import (
    NotionCollectionSchemaProperties,
    NotionFieldProps,
    NotionFieldShow,
)
from jupiter.remote.notion.infra.collections_manager import (
    NotionCollectionsManager,
    NotionCollectionItemNotFoundError,
)
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider


class NotionBigPlansManager(BigPlanNotionManager):
    """The centralised point for interacting with Notion big plans."""

    _KEY: ClassVar[str] = "big-plans"
    _PAGE_NAME: ClassVar[str] = "Big Plans"
    _PAGE_ICON: ClassVar[str] = "🌍"

    _STATUS: ClassVar[JSONDictType] = {
        "Not Started": {
            "name": BigPlanStatus.NOT_STARTED.for_notion(),
            "color": "orange",
            "in_board": True,
        },
        "Accepted": {
            "name": BigPlanStatus.ACCEPTED.for_notion(),
            "color": "orange",
            "in_board": True,
        },
        "In Progress": {
            "name": BigPlanStatus.IN_PROGRESS.for_notion(),
            "color": "blue",
            "in_board": True,
        },
        "Blocked": {
            "name": BigPlanStatus.BLOCKED.for_notion(),
            "color": "yellow",
            "in_board": True,
        },
        "Not Done": {
            "name": BigPlanStatus.NOT_DONE.for_notion(),
            "color": "red",
            "in_board": True,
        },
        "Done": {
            "name": BigPlanStatus.DONE.for_notion(),
            "color": "green",
            "in_board": True,
        },
    }

    _SCHEMA: ClassVar[JSONDictType] = {
        "title": {"name": "Name", "type": "title"},
        "status": {
            "name": "Status",
            "type": "select",
            "options": [
                {
                    "color": cast(Dict[str, str], v)["color"],
                    "id": str(uuid.uuid4()),
                    "value": cast(Dict[str, str], v)["name"],
                }
                for v in _STATUS.values()
            ],
        },
        "actionable-date": {"name": "Actionable Date", "type": "date"},
        "due-date": {"name": "Due Date", "type": "date"},
        "archived": {"name": "Archived", "type": "checkbox"},
        "project-ref-id": {"name": "Project Id", "type": "text"},
        "project-name": {
            "name": "Project",
            "type": "select",
            "options": [{"color": "gray", "id": str(uuid.uuid4()), "value": "None"}],
        },
        "last-edited-time": {"name": "Last Edited Time", "type": "last_edited_time"},
        "ref-id": {"name": "Ref Id", "type": "text"},
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("status", NotionFieldShow.SHOW),
        NotionFieldProps("actionable-date", NotionFieldShow.SHOW),
        NotionFieldProps("due-date", NotionFieldShow.SHOW),
        NotionFieldProps("archived", NotionFieldShow.SHOW),
        NotionFieldProps("project-ref-id", NotionFieldShow.HIDE),
        NotionFieldProps("project-name", NotionFieldShow.SHOW),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

    _KANBAN_WITH_PROJECT_SUBGROUP_FORMAT: ClassVar[JSONDictType] = {
        "board_groups": [
            {
                "property": "status",
                "type": "select",
                "value": cast(Dict[str, str], v)["name"],
                "hidden": not cast(Dict[str, bool], v)["in_board"],
            }
            for v in _STATUS.values()
        ]
        + [{"property": "status", "type": "select", "hidden": True}],
        "board_groups2": [
            {
                "property": "status",
                "value": {"type": "select", "value": cast(Dict[str, str], v)["name"]},
                "hidden": not cast(Dict[str, bool], v)["in_board"],
            }
            for v in _STATUS.values()
        ]
        + [{"property": "status", "value": {"type": "select"}, "hidden": True}],
        "board_columns_by": {
            "property": "status",
            "type": "select",
            "sort": {"type": "manual"},
            "hideEmptyGroups": False,
            "disableBoardColorColumns": False,
        },
        "collection_group_by": {
            "property": "project-name",
            "sort": {"type": "manual"},
            "type": "select",
        },
        "board_properties": [
            {"property": "status", "visible": False},
            {"property": "actionable-date", "visible": False},
            {"property": "due-date", "visible": True},
            {"property": "archived", "visible": False},
            {"property": "project-ref-id", "visible": False},
            {"property": "project-name", "visible": False},
            {"property": "last-edited-time", "visible": False},
        ],
        "board_cover_size": "small",
    }

    _FORMAT: ClassVar[JSONDictType] = {
        "board_groups": [
            {
                "property": "status",
                "type": "select",
                "value": cast(Dict[str, str], v)["name"],
                "hidden": not cast(Dict[str, bool], v)["in_board"],
            }
            for v in _STATUS.values()
        ]
        + [{"property": "status", "type": "select", "hidden": True}],
        "board_groups2": [
            {
                "property": "status",
                "value": {"type": "select", "value": cast(Dict[str, str], v)["name"]},
                "hidden": not cast(Dict[str, bool], v)["in_board"],
            }
            for v in _STATUS.values()
        ]
        + [{"property": "status", "value": {"type": "select"}, "hidden": True}],
        "board_properties": [
            {"property": "status", "visible": False},
            {"property": "actionable-date", "visible": False},
            {"property": "due-date", "visible": True},
            {"property": "archived", "visible": False},
            {"property": "project-ref-id", "visible": False},
            {"property": "project-name", "visible": True},
            {"property": "last-edited-time", "visible": False},
        ],
        "board_cover_size": "small",
    }

    _TIMELINE_BY_PROJECT_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Timeline By Project",
        "type": "timeline",
        "query2": {
            "timeline_by": "actionable-date",
            "timeline_by_end": "due-date",
            "aggregations": [{"property": "title", "aggregator": "count"}],
            "sort": [
                {"property": "actionable-date", "direction": "ascending"},
                {"property": "due-date", "direction": "ascending"},
                {"property": "status", "direction": "ascending"},
            ],
            "filter": {
                "operator": "and",
                "filters": [
                    {
                        "property": "archived",
                        "filter": {
                            "operator": "checkbox_is_not",
                            "value": {"type": "exact", "value": True},
                        },
                    }
                ],
            },
        },
        "format": {
            "collection_group_by": {
                "property": "project-name",
                "sort": {"type": "manual"},
                "type": "select",
            },
            "timeline_show_table": True,
            "timeline_properties": [
                {"property": "title", "visible": True},
                {"property": "status", "visible": True},
            ],
            "timeline_preference": {"zoomLevel": "year"},
            "timeline_table_properties": [
                {"width": 400, "property": "title", "visible": True}
            ],
        },
    }

    _TIMELINE_ALL_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Timeline All",
        "type": "timeline",
        "query2": {
            "timeline_by": "actionable-date",
            "timeline_by_end": "due-date",
            "aggregations": [{"property": "title", "aggregator": "count"}],
            "sort": [
                {"property": "actionable-date", "direction": "ascending"},
                {"property": "due-date", "direction": "ascending"},
                {"property": "status", "direction": "ascending"},
            ],
            "filter": {
                "operator": "and",
                "filters": [
                    {
                        "property": "archived",
                        "filter": {
                            "operator": "checkbox_is_not",
                            "value": {"type": "exact", "value": True},
                        },
                    }
                ],
            },
        },
        "format": {
            "timeline_preference": {"zoomLevel": "year"},
            "timeline_show_table": True,
            "timeline_properties": [
                {"property": "title", "visible": True},
                {"property": "status", "visible": True},
                {"property": "project-name", "visible": True},
            ],
            "timeline_table_properties": [
                {"width": 400, "property": "title", "visible": True}
            ],
        },
    }

    _KANBAN_BY_PROJECT_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban By Project",
        "type": "board",
        "query2": {
            "group_by": "status",
            "filter_operator": "and",
            "aggregations": [{"aggregator": "count"}],
            "sort": [{"property": "due-date", "direction": "ascending"}],
            "filter": {
                "operator": "and",
                "filters": [
                    {
                        "property": "archived",
                        "filter": {
                            "operator": "checkbox_is_not",
                            "value": {"type": "exact", "value": True},
                        },
                    }
                ],
            },
        },
        "format": _KANBAN_WITH_PROJECT_SUBGROUP_FORMAT,
    }

    _KANBAN_ALL_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Kanban All",
        "type": "board",
        "query2": {
            "group_by": "status",
            "filter_operator": "and",
            "aggregations": [{"aggregator": "count"}],
            "sort": [{"property": "due-date", "direction": "ascending"}],
            "filter": {
                "operator": "and",
                "filters": [
                    {
                        "property": "archived",
                        "filter": {
                            "operator": "checkbox_is_not",
                            "value": {"type": "exact", "value": True},
                        },
                    }
                ],
            },
        },
        "format": _FORMAT,
    }

    _DATABASE_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "Database",
        "type": "table",
        "format": {
            "table_properties": [
                {"width": 400, "property": "title", "visible": True},
                {"width": 100, "property": "ref-id", "visible": False},
                {"width": 100, "property": "status", "visible": True},
                {"width": 100, "property": "actionable-date", "visible": True},
                {"width": 100, "property": "due-date", "visible": True},
                {"width": 100, "property": "archived", "visible": True},
                {"width": 100, "property": "project-ref-id", "visible": True},
                {"width": 100, "property": "project-name", "visible": True},
                {"width": 100, "property": "last-edited-time", "visible": True},
            ]
        },
    }

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
        self,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        collections_manager: NotionCollectionsManager,
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._collections_manager = collections_manager

    def upsert_trunk(
        self, parent: NotionWorkspace, trunk: NotionBigPlanCollection
    ) -> None:
        """Upsert the Notion-side big plan."""
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{trunk.ref_id}"),
            parent_page_notion_id=parent.notion_id,
            name=self._PAGE_NAME,
            icon=self._PAGE_ICON,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[
                (
                    "timeline_by_project_view_id",
                    NotionBigPlansManager._TIMELINE_BY_PROJECT_VIEW_SCHEMA,
                ),
                (
                    "timeline_all_view_id",
                    NotionBigPlansManager._TIMELINE_ALL_VIEW_SCHEMA,
                ),
                (
                    "kanban_by_project_view_id",
                    NotionBigPlansManager._KANBAN_BY_PROJECT_VIEW_SCHEMA,
                ),
                ("kanban_all_view_id", NotionBigPlansManager._KANBAN_ALL_VIEW_SCHEMA),
                ("database_view_id", NotionBigPlansManager._DATABASE_VIEW_SCHEMA),
            ],
        )

    def upsert_big_plans_project_field_options(
        self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]
    ) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""
        inbox_big_plan_options = [
            {
                "color": self._get_stable_color(str(pl.notion_link_uuid)),
                "id": str(pl.notion_link_uuid),
                "value": format_name_for_option(pl.name),
            }
            for pl in project_labels
        ]

        new_schema: JSONDictType = copy.deepcopy(self._SCHEMA)
        new_schema["project-name"]["options"] = inbox_big_plan_options  # type: ignore

        self._collections_manager.save_collection_no_merge(
            NotionLockKey(f"{self._KEY}:{ref_id}"),
            self._PAGE_NAME,
            self._PAGE_ICON,
            new_schema,
            "project-name",
        )

        timeline_new_view: JSONDictType = copy.deepcopy(
            NotionBigPlansManager._TIMELINE_BY_PROJECT_VIEW_SCHEMA
        )
        timeline_new_view["format"]["collection_groups"] = [  # type: ignore
            {
                "property": "project-name",
                "value": {"type": "select", "value": format_name_for_option(pl.name)},
                "hidden": False,
            }
            for pl in sorted(project_labels, key=lambda x: x.created_time)
        ] + [{"property": "project-name", "value": {"type": "select"}, "hidden": True}]

        self._collections_manager.quick_update_view_for_collection(
            NotionLockKey(f"{self._KEY}:{ref_id}"),
            "timeline_by_project_view_id",
            timeline_new_view,
        )

        kanban_new_view: JSONDictType = copy.deepcopy(
            NotionBigPlansManager._KANBAN_BY_PROJECT_VIEW_SCHEMA
        )
        kanban_new_view["format"]["collection_groups"] = [  # type: ignore
            {
                "property": "project-name",
                "value": {"type": "select", "value": format_name_for_option(pl.name)},
                "hidden": False,
            }
            for pl in sorted(project_labels, key=lambda x: x.created_time)
        ] + [{"property": "project-name", "value": {"type": "select"}, "hidden": True}]

        self._collections_manager.quick_update_view_for_collection(
            NotionLockKey(f"{self._KEY}:{ref_id}"),
            "kanban_by_project_view_id",
            kanban_new_view,
        )

    def upsert_leaf(
        self,
        trunk_ref_id: EntityId,
        leaf: NotionBigPlan,
    ) -> NotionBigPlan:
        """Upsert a big plan."""
        link = self._collections_manager.upsert_collection_item(
            timezone=self._global_properties.timezone,
            schema=self._SCHEMA,
            key=NotionLockKey(f"{leaf.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            new_leaf=leaf,
        )
        return link.item_info

    def save_leaf(
        self,
        trunk_ref_id: EntityId,
        leaf: NotionBigPlan,
    ) -> NotionBigPlan:
        """Update the Notion-side big plan with new data."""
        try:
            link = self._collections_manager.save_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                key=NotionLockKey(f"{leaf.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
                row=leaf,
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionBigPlanNotFoundError(
                f"Notion big plan with id {leaf.ref_id} could not be found"
            ) from err

    def load_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> NotionBigPlan:
        """Retrieve the Notion-side big plan associated with a particular entity."""
        try:
            link = self._collections_manager.load_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionBigPlan,
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionBigPlanNotFoundError(
                f"Notion big plan with id {leaf_ref_id} could not be found"
            ) from err

    def load_all_leaves(self, trunk_ref_id: EntityId) -> Iterable[NotionBigPlan]:
        """Retrieve all the Notion-side big plans."""
        return [
            l.item_info
            for l in self._collections_manager.load_all_collection_items(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionBigPlan,
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
        ]

    def remove_leaf(
        self, trunk_ref_id: EntityId, leaf_ref_id: Optional[EntityId]
    ) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            )
        except NotionCollectionItemNotFoundError as err:
            raise NotionBigPlanNotFoundError(
                f"Notion big plan with id {leaf_ref_id} could not be found"
            ) from err

    def drop_all_leaves(self, trunk_ref_id: EntityId) -> None:
        """Remove all big plans Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the big plans tasks."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def load_all_saved_notion_ids(self, trunk_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )

    def link_local_and_notion_leaves(
        self, trunk_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId
    ) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}"),
            key=NotionLockKey(f"{ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id,
        )

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
            "red",
        ]
        return colors[
            hashlib.sha256(option_id.encode("utf-8")).digest()[0] % len(colors)
        ]
