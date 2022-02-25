"""A repository of metric entries."""
import abc
from typing import Optional, List, Iterable

from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


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
    def find_all(
            self,
            metric_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric - an irreversible operation."""
