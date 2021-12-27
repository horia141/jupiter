"""A manager of Notion-side metrics."""
import abc
from typing import Iterable, Optional

from domain.metrics.notion_metric import NotionMetric
from domain.metrics.notion_metric_entry import NotionMetricEntry
from domain.workspaces.notion_workspace import NotionWorkspace
from framework.base.entity_id import EntityId
from framework.base.notion_id import NotionId


class NotionMetricNotFoundError(Exception):
    """Error raised when a Notion-side metric does not exist (but should)."""


class NotionMetricEntryNotFoundError(Exception):
    """Error raised when a Notion-side metric entry does not exist (but should)."""


class MetricNotionManager(abc.ABC):
    """A manager of Notion-side metrics."""

    @abc.abstractmethod
    def upsert_root_page(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root page structure for vacations."""

    @abc.abstractmethod
    def upsert_metric(self, metric: NotionMetric) -> NotionMetric:
        """Upsert a metric on Notion-side."""

    @abc.abstractmethod
    def save_metric(self, metric: NotionMetric) -> NotionMetric:
        """Load a metric on Notion-side."""

    @abc.abstractmethod
    def load_metric(self, ref_id: EntityId) -> NotionMetric:
        """Load a metric on Notion-side."""

    @abc.abstractmethod
    def remove_metric(self, ref_id: EntityId) -> None:
        """Remove a metric on Notion-side."""

    @abc.abstractmethod
    def upsert_metric_entry(self, metric_ref_id: EntityId, metric_entry: NotionMetricEntry) -> NotionMetricEntry:
        """Upsert a metric entry on Notion-side."""

    @abc.abstractmethod
    def save_metric_entry(self, metric_ref_id: EntityId, metric_entry: NotionMetricEntry) -> NotionMetricEntry:
        """Save an already existing metric entry on Notion-side."""

    @abc.abstractmethod
    def load_metric_entry(self, metric_ref_id: EntityId, ref_id: EntityId) -> NotionMetricEntry:
        """Load a particular metric entry."""

    @abc.abstractmethod
    def load_all_metric_entries(self, metric_ref_id: EntityId) -> Iterable[NotionMetricEntry]:
        """Load all metric entries."""

    @abc.abstractmethod
    def remove_metric_entry(self, metric_ref_id: EntityId, metric_entry_ref_id: Optional[EntityId]) -> None:
        """Remove a metric on Notion-side."""

    @abc.abstractmethod
    def drop_all_metric_entries(self, metric_ref_id: EntityId) -> None:
        """Remove all metric entries Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_entries_for_metric(
            self, metric_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_metric_entries_ref_ids(self, metric_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the metric entries."""

    @abc.abstractmethod
    def load_all_saved_metric_entries_notion_ids(self, metric_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion ids for the metric entries."""
