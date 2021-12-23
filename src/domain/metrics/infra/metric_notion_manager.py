"""A manager of Notion-side metrics."""
import abc
from typing import Iterable, Optional

from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from domain.metrics.notion_metric import NotionMetric
from domain.metrics.notion_metric_entry import NotionMetricEntry
from domain.workspaces.notion_workspace import NotionWorkspace
from framework.entity_id import EntityId
from framework.notion import NotionId


class MetricNotionManager(abc.ABC):
    """A manager of Notion-side metrics."""

    @abc.abstractmethod
    def upsert_root_page(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root page structure for vacations."""

    @abc.abstractmethod
    def upsert_metric(self, metric: Metric) -> NotionMetric:
        """Upsert a metric on Notion-side."""

    @abc.abstractmethod
    def save_metric(self, metric: NotionMetric) -> NotionMetric:
        """Load a metric on Notion-side."""

    @abc.abstractmethod
    def load_metric(self, metric: Metric) -> NotionMetric:
        """Load a metric on Notion-side."""

    @abc.abstractmethod
    def remove_metric(self, metric: Metric) -> None:
        """Remove a metric on Notion-side."""

    @abc.abstractmethod
    def upsert_metric_entry(self, metric_entry: MetricEntry) -> None:
        """Upsert a metric entry on Notion-side."""

    @abc.abstractmethod
    def save_metric_entry(self, metric: Metric, metric_entry: NotionMetricEntry) -> NotionMetricEntry:
        """Save an already existing metric entry on Notion-side."""

    @abc.abstractmethod
    def load_all_metric_entries(self, metric: Metric) -> Iterable[NotionMetricEntry]:
        """Load all metric entries."""

    @abc.abstractmethod
    def remove_metric_entry(self, metric_ref_id: EntityId, metric_entry_ref_id: Optional[EntityId]) -> None:
        """Remove a metric on Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_entries_for_metric(
            self, metric_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_metric_entries_ref_ids(self, metric: Metric) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the metric entries."""

    @abc.abstractmethod
    def load_all_saved_metric_entries_notion_ids(self, metric: Metric) -> Iterable[NotionId]:
        """Retrieve all the saved Notion ids for the metric entries."""

    @abc.abstractmethod
    def drop_all_metric_entries(self, metric: Metric) -> None:
        """Remove all metric entries Notion-side."""
