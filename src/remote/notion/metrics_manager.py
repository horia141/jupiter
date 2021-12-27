"""The centralised point for interacting with Notion metrics."""
import typing
from typing import ClassVar, Final

from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from domain.adate import ADate
from domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricNotFoundError, \
    NotionMetricEntryNotFoundError
from domain.metrics.notion_metric import NotionMetric
from domain.metrics.notion_metric_entry import NotionMetricEntry
from domain.workspaces.notion_workspace import NotionWorkspace
from framework.base.entity_id import EntityId
from framework.base.notion_id import NotionId
from framework.base.timestamp import Timestamp
from framework.json import JSONDictType
from remote.notion.common import NotionPageLink, NotionLockKey
from remote.notion.infra.client import NotionCollectionSchemaProperties, NotionFieldShow, NotionFieldProps
from remote.notion.infra.collections_manager import CollectionsManager, NotionCollectionNotFoundError, \
    NotionCollectionItemNotFoundError
from remote.notion.infra.pages_manager import PagesManager
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider


class NotionMetricManager(MetricNotionManager):
    """The centralised point for interacting with Notion metrics."""

    _KEY: ClassVar[str] = "metrics"
    _PAGE_NAME: ClassVar[str] = "Metrics"

    _SCHEMA: ClassVar[JSONDictType] = {
        "collection-time": {
            "name": "Collection Time",
            "type": "date"
        },
        "value": {
            "name": "Value",
            "type": "number"
        },
        "title": {
            "name": "Notes",
            "type": "title"
        },
        "ref-id": {
            "name": "Ref Id",
            "type": "text"
        },
        "archived": {
            "name": "Archived",
            "type": "checkbox"
        },
        "last-edited-time": {
            "name": "Last Edited Time",
            "type": "last_edited_time"
        },
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
            "aggregations": [{
                "aggregator": "count"
            }],
            "sort": [{
                "property": "collection-time",
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
            "table_properties": [{
                "width": 100,
                "property": "collection-time",
                "visible": True
            }, {
                "width": 100,
                "property": "value",
                "visible": True
            }, {
                "width": 100,
                "property": "title",
                "visible": True
            }, {
                "width": 100,
                "property": "ref-id",
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
    _pages_manager: Final[PagesManager]
    _collections_manager: Final[CollectionsManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider, pages_manager: PagesManager,
            collections_manager: CollectionsManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._pages_manager = pages_manager
        self._collections_manager = collections_manager

    def upsert_root_page(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root page for the metrics section."""
        self._pages_manager.upsert_page(
            NotionLockKey(self._KEY), self._PAGE_NAME, NotionPageLink(notion_workspace.notion_id))

    def upsert_metric(self, metric: NotionMetric) -> NotionMetric:
        """Upsert the Notion-side metric."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        metric_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{metric.ref_id}"),
            parent_page=root_page,
            name=metric.name,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "database_view_id": self._DATABASE_VIEW_SCHEMA
            })

        return NotionMetric(
            name=metric.name,
            ref_id=metric.ref_id,
            notion_id=metric_link.collection_id)

    def save_metric(self, metric: NotionMetric) -> NotionMetric:
        """Save a metric collection."""
        try:
            self._collections_manager.save_collection(
                key=NotionLockKey(f"{self._KEY}:{metric.ref_id}"),
                new_name=metric.name,
                new_schema=self._SCHEMA)
        except NotionCollectionNotFoundError as err:
            raise NotionMetricNotFoundError(f"Could not find metric with id {metric.ref_id} locally") from err
        return metric

    def load_metric(self, ref_id: EntityId) -> NotionMetric:
        """Load a metric collection."""
        try:
            metric_link = self._collections_manager.load_collection(
                key=NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionMetricNotFoundError(f"Could not find metric with id {ref_id} locally") from err

        return NotionMetric(
            name=metric_link.name,
            ref_id=ref_id,
            notion_id=metric_link.collection_id)

    def remove_metric(self, ref_id: EntityId) -> None:
        """Remove a metric on Notion-side."""
        try:
            self._collections_manager.remove_collection(NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionCollectionNotFoundError as err:
            raise NotionMetricNotFoundError(f"Could not find metric with id {ref_id} locally") from err

    def upsert_metric_entry(self, metric_ref_id: EntityId, metric_entry: NotionMetricEntry) -> NotionMetricEntry:
        """Upsert a metric entry on Notion-side."""
        return self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{metric_entry.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            new_row=metric_entry,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def save_metric_entry(
            self, metric_ref_id: EntityId, metric_entry: NotionMetricEntry) -> NotionMetricEntry:
        """Update the Notion-side metric with new data."""
        try:
            return self._collections_manager.save_collection_item(
                key=NotionLockKey(f"{metric_entry.ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
                row=metric_entry,
                copy_row_to_notion_row=self._copy_row_to_notion_row)
        except NotionCollectionItemNotFoundError as err:
            raise NotionMetricEntryNotFoundError(
                f"Notion metric entry with id {metric_entry.ref_id} does not exist") from err

    def load_metric_entry(self, metric_ref_id: EntityId, ref_id: EntityId) -> NotionMetricEntry:
        """Load a particular metric entry."""
        try:
            return self._collections_manager.load_collection_item(
                key=NotionLockKey(f"{ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
                copy_notion_row_to_row=self._copy_notion_row_to_row)
        except NotionCollectionItemNotFoundError as err:
            raise NotionMetricEntryNotFoundError(
                f"Notion metric entry with id {ref_id} does not exist") from err

    def load_all_metric_entries(self, metric_ref_id: EntityId) -> typing.Iterable[NotionMetricEntry]:
        """Retrieve all the Notion-side metric entrys."""
        return self._collections_manager.load_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def remove_metric_entry(self, metric_ref_id: EntityId, metric_entry_ref_id: typing.Optional[EntityId]) -> None:
        """Remove a metric on Notion-side."""
        try:
            self._collections_manager.remove_collection_item(
                key=NotionLockKey(f"{metric_entry_ref_id}"),
                collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))
        except NotionCollectionItemNotFoundError as err:
            raise NotionMetricEntryNotFoundError(
                f"Notion metric entry with id {metric_ref_id} does not exist") from err

    def drop_all_metric_entries(self, metric_ref_id: EntityId) -> None:
        """Remove all metric entries Notion-side."""
        self._collections_manager.drop_all_collection_items(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def link_local_and_notion_entries_for_metric(
            self, metric_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries_for_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def load_all_saved_metric_entries_ref_ids(self, metric_ref_id: EntityId) -> typing.Iterable[EntityId]:
        """Retrieve all the saved ref ids for the metric entries."""
        return self._collections_manager.load_all_collection_items_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def load_all_saved_metric_entries_notion_ids(self, metric_ref_id: EntityId) -> typing.Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these metrics entries."""
        return self._collections_manager.load_all_collection_items_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: NotionMetricEntry, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.collection_time = row.collection_time.to_notion(self._global_properties.timezone)
            notion_row.value = row.value
            notion_row.title = row.notes if row.notes else ""
            notion_row.archived = row.archived
            notion_row.last_edited_time = row.last_edited_time.to_notion(self._global_properties.timezone)
            notion_row.ref_id = row.ref_id

        return notion_row

    def _copy_notion_row_to_row(self, notion_row: CollectionRowBlock) -> NotionMetricEntry:
        """Copy the fields of the local row to the actual Notion structure."""
        return NotionMetricEntry(
            collection_time=ADate.from_notion(self._global_properties.timezone, notion_row.collection_time),
            value=notion_row.value,
            notes=notion_row.title if typing.cast(str, notion_row.title).strip() != "" else None,
            archived=notion_row.archived,
            last_edited_time=Timestamp.from_notion(notion_row.last_edited_time),
            ref_id=notion_row.ref_id,
            notion_id=NotionId.from_raw(notion_row.id))
