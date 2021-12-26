"""A repository of metric entries."""
import abc
from typing import Optional, List, Iterable

from domain.metrics.metric_entry import MetricEntry
from framework.base.entity_id import EntityId
from framework.storage import Repository


class MetricEntryNotFoundError(Exception):
    """Error raised when a metric entry does not exist."""


class MetricEntryRepository(Repository, abc.ABC):
    """A repository of metric entries."""

    @abc.abstractmethod
    def create(self, metric_entry: MetricEntry) -> MetricEntry:
        """Create a metric entry."""

    @abc.abstractmethod
    def save(self, metric_entry: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> MetricEntry:
        """Load a given metric entry."""

    @abc.abstractmethod
    def find_all_for_metric(self, metric_ref_id: EntityId, allow_archived: bool = False) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None) -> List[MetricEntry]:
        """Find all metric entries matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric - an irreversible operation."""
