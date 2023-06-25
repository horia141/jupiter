"""A repository of metric entries."""
import abc

from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class MetricEntryNotFoundError(LeafEntityNotFoundError):
    """Error raised when a metric entry does not exist."""


class MetricEntryRepository(LeafEntityRepository[MetricEntry], abc.ABC):
    """A repository of metric entries."""
