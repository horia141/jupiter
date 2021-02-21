"""A manager of Notion-side metrics."""
import abc

from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry


class MetricNotionManager(abc.ABC):
    """A manager of Notion-side metrics."""

    @abc.abstractmethod
    def upsert_metric(self, metric: Metric) -> None:
        """Upsert a metric on Notion-side."""

    @abc.abstractmethod
    def remove_metric(self, metric: Metric) -> None:
        """Remove a metric on Notion-side."""

    @abc.abstractmethod
    def upsert_metric_entry(self, metric_entry: MetricEntry) -> None:
        """Upsert a metric entry on Notion-side."""

    @abc.abstractmethod
    def remove_metric_entry(self, metric_entry: MetricEntry) -> None:
        """Remove a metric on Notion-side."""
