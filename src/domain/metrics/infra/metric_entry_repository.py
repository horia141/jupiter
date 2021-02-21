"""A repository of metric entries."""
import abc
from typing import Optional, List, Iterable

from domain.metrics.metric_entry import MetricEntry
from models.basic import EntityId


class MetricEntryRepository(abc.ABC):
    """A repository of metric entries."""

    @abc.abstractmethod
    def create(self, metric_entry: MetricEntry) -> MetricEntry:
        """Create a metric entry."""

    @abc.abstractmethod
    def save(self, metric_entry: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId) -> MetricEntry:
        """Load a given metric entry."""

    @abc.abstractmethod
    def find_all_for_metric(self, metric_ref_id: EntityId) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""

    @abc.abstractmethod
    def find_all(self, allow_archived: bool, filter_metric_ref_ids: Optional[Iterable[EntityId]]) -> List[MetricEntry]:
        """Find all metric entries matching some criteria."""

    @abc.abstractmethod
    def remove(self, metric_entry: MetricEntry) -> None:
        """Hard remove a metric - an irreversible operation."""
