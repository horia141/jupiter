"""A repository of metric entries."""
import abc

from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class MetricEntryNotFoundError(LeafEntityNotFoundError):
    """Error raised when a metric entry does not exist."""


class MetricEntryRepository(LeafEntityRepository[MetricEntry], abc.ABC):
    """A repository of metric entries."""
