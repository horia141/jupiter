"""The centralised point for interacting with Notion metrics."""
import logging
import typing
from typing import ClassVar, Final

from jupiter.domain.metrics.infra.metric_notion_manager import (
    MetricNotionManager,
    NotionMetricNotFoundError,
    NotionMetricEntryNotFoundError,
)
from jupiter.domain.metrics.notion_metric import NotionMetric
from jupiter.domain.metrics.notion_metric_collection import NotionMetricCollection
from jupiter.domain.metrics.notion_metric_entry import NotionMetricEntry
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.json import JSONDictType
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.client import (
    NotionCollectionSchemaProperties,
    NotionFieldShow,
    NotionFieldProps,
)
from jupiter.remote.notion.infra.collections_manager import (
    NotionCollectionsManager,
    NotionCollectionNotFoundError,
    NotionCollectionItemNotFoundError,
)
from jupiter.remote.notion.infra.pages_manager import NotionPagesManager
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class NotionMetricsManager(MetricNotionManager):
    """The centralised point for interacting with Notion metrics."""

    _KEY: ClassVar[str] = "metrics"
    _PAGE_NAME: ClassVar[str] = "Metrics"
    _PAGE_ICON: ClassVar[str] = "📈"

    _SCHEMA: ClassVar[JSONDictType] = {
        "collection-time": {"name": "Collection Time", "type": "date"},
        "value": {"name": "Value", "type": "number"},
        "title": {"name": "Notes", "type": "title"},
        "ref-id": {"name": "Ref Id", "type": "text"},
        "archived": {"name": "Archived", "type": "checkbox"},
        "last-edited-time": {"name": "Last Edited Time", "type": "last_edited_time"},
    }

    _SCHEMA_PROPERTIES: ClassVar[NotionCollectionSchemaProperties] = [
        NotionFieldProps("collection-time", NotionFieldShow.SHOW),
        NotionFieldProps("value", NotionFieldShow.SHOW),
        NotionFieldProps("title", NotionFieldShow.SHOW),
        NotionFieldProps("archived", NotionFieldShow.SHOW),
        NotionFieldProps("ref-id", NotionFieldShow.SHOW),
        NotionFieldProps("last-edited-time", NotionFieldShow.HIDE),
    ]

    _DATABASE_VIEW_SCHEMA: ClassVar[JSONDictType] = {
        "name": "All",
        "type": "table",
        "query2": {
            "filter_operator": "and",
            "aggregations": [{"aggregator": "count"}],
            "sort": [{"property": "collection-time", "direction": "ascending"}],
        },
        "format": {
            "table_properties": [
                {"width": 100, "property": "collection-time", "visible": True},
                {"width": 100, "property": "value", "visible": True},
                {"width": 100, "property": "title", "visible": True},
                {"width": 100, "property": "ref-id", "visible": True},
                {"width": 100, "property": "archived", "visible": True},
                {"width": 100, "property": "last-edited-time", "visible": True},
            ]
        },
    }

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _pages_manager: Final[NotionPagesManager]
    _collections_manager: Final[NotionCollectionsManager]

    def __init__(
        self,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        pages_manager: NotionPagesManager,
        collections_manager: NotionCollectionsManager,
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._pages_manager = pages_manager
        self._collections_manager = collections_manager

    def upsert_trunk(
        self, parent: NotionWorkspace, trunk: NotionMetricCollection
    ) -> None:
        """Upsert the root page for the metrics section."""
        self._pages_manager.upsert_page(
            NotionLockKey(f"{self._KEY}:{trunk.ref_id}"),
            self._PAGE_NAME,
            parent.notion_id,
            self._PAGE_ICON,
        )

    def upsert_branch(
        self, trunk_ref_id: EntityId, branch: NotionMetric
    ) -> NotionMetric:
        """Upsert the Notion-side metric."""
        root_page = self._pages_manager.get_page(
            NotionLockKey(f"{self._KEY}:{trunk_ref_id}")
        )
        branch_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch.ref_id}"),
            parent_page_notion_id=root_page.notion_id,
            name=branch.name,
            icon=branch.icon,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas=[("database_view_id", self._DATABASE_VIEW_SCHEMA)],
        )

        return NotionMetric(
            name=branch.name,
            icon=branch.icon,
            ref_id=branch.ref_id,
            notion_id=branch_link.collection_notion_id,
        )

    def save_branch(self, trunk_ref_id: EntityId, branch: NotionMetric) -> NotionMetric:
        """Save a metric collection."""
        try:
            self._collections_manager.save_collection(
                key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch.ref_id}"),
                new_name=branch.name,
                new_icon=branch.icon,
                new_schema=self._SCHEMA,
            )
        except NotionCollectionNotFoundError as err:
            raise NotionMetricNotFoundError(
                f"Could not find metric with id {branch.ref_id} locally"
            ) from err
        return branch

    def load_branch(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> NotionMetric:
        """Load a metric collection."""
        try:
            branch_link = self._collections_manager.load_collection(
                key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}")
            )
        except NotionCollectionNotFoundError as err:
            raise NotionMetricNotFoundError(
                f"Could not find metric with id {branch_ref_id} locally"
            ) from err

        return NotionMetric(
            name=branch_link.name,
            icon=branch_link.icon,
            ref_id=branch_ref_id,
            notion_id=branch_link.collection_notion_id,
        )

    def remove_branch(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove a metric on Notion-side."""
        try:
            self._collections_manager.remove_collection(
                NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}")
            )
        except NotionCollectionNotFoundError as err:
            raise NotionMetricNotFoundError(
                f"Could not find metric with id {branch_ref_id} locally"
            ) from err

    def upsert_leaf(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf: NotionMetricEntry,
    ) -> NotionMetricEntry:
        """Upsert a metric entry on Notion-side."""
        link = self._collections_manager.upsert_collection_item(
            timezone=self._global_properties.timezone,
            schema=self._SCHEMA,
            key=NotionLockKey(f"{leaf.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}"),
            new_leaf=leaf,
        )
        return link.item_info

    def save_leaf(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf: NotionMetricEntry,
    ) -> NotionMetricEntry:
        """Update the Notion-side metric with new data."""
        try:
            link = self._collections_manager.save_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                key=NotionLockKey(f"{leaf.ref_id}"),
                collection_key=NotionLockKey(
                    f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}"
                ),
                row=leaf,
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionMetricEntryNotFoundError(
                f"Notion metric entry with id {leaf.ref_id} does not exist"
            ) from err

    def load_leaf(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf_ref_id: EntityId
    ) -> NotionMetricEntry:
        """Load a particular metric entry."""
        try:
            link = self._collections_manager.load_collection_item(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionMetricEntry,
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(
                    f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}"
                ),
            )
            return link.item_info
        except NotionCollectionItemNotFoundError as err:
            raise NotionMetricEntryNotFoundError(
                f"Notion metric entry with id {leaf_ref_id} does not exist"
            ) from err

    def load_all_leaves(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> typing.Iterable[NotionMetricEntry]:
        """Retrieve all the Notion-side metric entrys."""
        return [
            l.item_info
            for l in self._collections_manager.load_all_collection_items(
                timezone=self._global_properties.timezone,
                schema=self._SCHEMA,
                ctor=NotionMetricEntry,
                collection_key=NotionLockKey(
                    f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}"
                ),
            )
        ]

    def remove_leaf(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf_ref_id: typing.Optional[EntityId],
    ) -> None:
        """Remove a metric on Notion-side."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{leaf_ref_id}"),
                collection_key=NotionLockKey(
                    f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}"
                ),
            )
        except NotionCollectionItemNotFoundError as err:
            raise NotionMetricEntryNotFoundError(
                f"Notion metric entry with id {branch_ref_id} does not exist"
            ) from err

    def drop_all_leaves(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove all metric entries Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}")
        )

    def load_all_saved_ref_ids(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> typing.Iterable[EntityId]:
        """Retrieve all the saved ref ids for the metric entries."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}")
        )

    def load_all_saved_notion_ids(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> typing.Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these metrics entries."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}")
        )

    def link_local_and_notion_leaves(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf_ref_id: EntityId,
        notion_id: NotionId,
    ) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            key=NotionLockKey(f"{leaf_ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{trunk_ref_id}:{branch_ref_id}"),
            ref_id=leaf_ref_id,
            notion_id=notion_id,
        )
