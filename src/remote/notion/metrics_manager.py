"""The centralised point for interacting with Notion metrics."""
from dataclasses import dataclass
from typing import ClassVar, Final
import typing

from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from domain.metrics.metric import Metric
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.metric_entry import MetricEntry
from models.basic import Timestamp, EntityId, BasicValidator, ADate
from remote.notion.common import NotionPageLink, NotionLockKey, NotionId
from remote.notion.infra.client import NotionCollectionSchemaProperties, NotionFieldShow, NotionFieldProps
from remote.notion.infra.collections_manager import CollectionsManager, BaseItem
from remote.notion.infra.pages_manager import PagesManager
from utils.storage import JSONDictType
from utils.time_provider import TimeProvider


@dataclass()
class _MetricNotionCollection(BaseItem):
    """A metric collection on Notion side."""

    name: str


@dataclass()
class _MetricNotionRow(BaseItem):
    """A metric entry on Notion side."""

    collection_time: ADate
    value: float
    notes: typing.Optional[str]
    archived: bool
    last_edited_time: Timestamp


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

    _time_provider: Final[TimeProvider]
    _basic_validator: Final[BasicValidator]
    _pages_manager: Final[PagesManager]
    _collections_manager: Final[CollectionsManager]

    def __init__(
            self, time_provider: TimeProvider, basic_validator: BasicValidator, pages_manager: PagesManager,
            collections_manager: CollectionsManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._basic_validator = basic_validator
        self._pages_manager = pages_manager
        self._collections_manager = collections_manager

    def upsert_root_page(self, parent_page_link: NotionPageLink) -> None:
        """Upsert the root page for the metrics section."""
        self._pages_manager.upsert_page(NotionLockKey(self._KEY), self._PAGE_NAME, parent_page_link)

    def upsert_metric(self, metric: Metric) -> None:
        """Upsert the Notion-side metric."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{metric.ref_id}"),
            parent_page=root_page,
            name=metric.name,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "database_view_id": self._DATABASE_VIEW_SCHEMA
            })

    def remove_metric(self, metric: Metric) -> None:
        """Remove a metric on Notion-side."""
        self._collections_manager.remove_collection(NotionLockKey(f"{self._KEY}:{metric.ref_id}"))

    def upsert_metric_entry(self, metric_entry: MetricEntry) -> None:
        """Upsert a metric entry on Notion-side."""
        new_row = _MetricNotionRow(
            collection_time=metric_entry.collection_time,
            value=metric_entry.value,
            notes=metric_entry.notes,
            archived=metric_entry.archived,
            last_edited_time=self._time_provider.get_current_time(),
            ref_id=metric_entry.ref_id,
            notion_id=typing.cast(NotionId, None))
        self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{metric_entry.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_entry.metric_ref_id}"),
            new_row=new_row,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def remove_metric_entry(self, metric_entry: MetricEntry) -> None:
        """Remove a metric on Notion-side."""
        self._collections_manager.hard_remove(
            key=NotionLockKey(f"{metric_entry.ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_entry.metric_ref_id}"))

    # Old stuff

    def upsert_metric_collection(self, ref_id: EntityId, name: str) -> _MetricNotionCollection:
        """Upsert the Notion-side metric."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        collection_link = self._collections_manager.upsert_collection(
            key=NotionLockKey(f"{self._KEY}:{ref_id}"),
            parent_page=root_page,
            name=name,
            schema=self._SCHEMA,
            schema_properties=self._SCHEMA_PROPERTIES,
            view_schemas={
                "database_view_id": self._DATABASE_VIEW_SCHEMA
            })

        return _MetricNotionCollection(
            name=name,
            ref_id=ref_id,
            notion_id=collection_link.collection_id)

    def load_metric_collection(self, metric_ref_id: EntityId) -> _MetricNotionCollection:
        """Load a metric collection."""
        metric_link = self._collections_manager.get_collection(
            key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

        return _MetricNotionCollection(
            name=metric_link.name,
            ref_id=metric_ref_id,
            notion_id=metric_link.collection_id)

    def save_metric_collection(self, metric: _MetricNotionCollection) -> None:
        """Save a metric collection."""
        self._collections_manager.update_collection(
            key=NotionLockKey(f"{self._KEY}:{metric.ref_id}"),
            new_name=metric.name,
            new_schema=self._SCHEMA)

    def hard_remove_metric_collection(self, ref_id: EntityId) -> None:
        """Hard remove a metric entry."""
        self._collections_manager.remove_collection(NotionLockKey(f"{self._KEY}:{ref_id}"))

    def upsert_metric_entry_old(
            self, metric_ref_id: EntityId, ref_id: EntityId, collection_time: Timestamp, value: float,
            notes: typing.Optional[str], archived: bool) -> _MetricNotionRow:
        """Upsert the Notion-side metric entry."""
        new_row = _MetricNotionRow(
            collection_time=collection_time,
            value=value,
            notes=notes,
            archived=archived,
            last_edited_time=self._time_provider.get_current_time(),
            ref_id=ref_id,
            notion_id=typing.cast(NotionId, None))
        self._collections_manager.upsert_collection_item(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            new_row=new_row,
            copy_row_to_notion_row=self._copy_row_to_notion_row)
        return new_row

    def load_all_metric_entries(self, metric_ref_id: EntityId) -> typing.Iterable[_MetricNotionRow]:
        """Retrieve all the Notion-side metric entrys."""
        return self._collections_manager.load_all(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            copy_notion_row_to_row=self._copy_notion_row_to_row)

    def save_metric_entry(
            self, metric_ref_id: EntityId, ref_id: EntityId,
            new_metric_entry_row: _MetricNotionRow) -> _MetricNotionRow:
        """Update the Notion-side metric with new data."""
        return self._collections_manager.save(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            row=new_metric_entry_row,
            copy_row_to_notion_row=self._copy_row_to_notion_row)

    def hard_remove_metric_entry(self, metric_ref_id: EntityId, ref_id: EntityId) -> None:
        """Hard remove a particular metric entry."""
        self._collections_manager.hard_remove(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def load_all_saved_metric_entries_notion_ids(self, metric_ref_id: EntityId) -> typing.Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these metrics entries."""
        return self._collections_manager.load_all_saved_notion_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def load_all_saved_metric_entries_ref_ids(self, metric_ref_id: EntityId) -> typing.Iterable[EntityId]:
        """Retrieve all the saved ref ids for the metric entries."""
        return self._collections_manager.load_all_saved_ref_ids(
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def drop_all_metric_entries(self, metric_ref_id: EntityId) -> None:
        """Remove all metric entries Notion-side."""
        self._collections_manager.drop_all(collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"))

    def link_local_and_notion_entries_for_metric(
            self, metric_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        self._collections_manager.quick_link_local_and_notion_entries(
            key=NotionLockKey(f"{ref_id}"),
            collection_key=NotionLockKey(f"{self._KEY}:{metric_ref_id}"),
            ref_id=ref_id,
            notion_id=notion_id)

    def _copy_row_to_notion_row(
            self, client: NotionClient, row: _MetricNotionRow, notion_row: CollectionRowBlock) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        with client.with_transaction():
            notion_row.collection_time = self._basic_validator.adate_to_notion(row.collection_time)
            notion_row.value = row.value
            notion_row.title = row.notes if row.notes else ""
            notion_row.archived = row.archived
            notion_row.last_edited_time = self._basic_validator.timestamp_to_notion_timestamp(row.last_edited_time)
            notion_row.ref_id = row.ref_id

        return notion_row

    def _copy_notion_row_to_row(self, notion_row: CollectionRowBlock) -> _MetricNotionRow:
        """Copy the fields of the local row to the actual Notion structure."""
        return _MetricNotionRow(
            collection_time=self._basic_validator.adate_from_notion(notion_row.collection_time),
            value=notion_row.value,
            notes=notion_row.title if typing.cast(str, notion_row.title).strip() != "" else None,
            archived=notion_row.archived,
            last_edited_time=self._basic_validator.timestamp_from_notion_timestamp(notion_row.last_edited_time),
            ref_id=notion_row.ref_id,
            notion_id=notion_row.id)
