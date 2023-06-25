"""A repository for metric collections."""
import abc

from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.framework.repository import (
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class MetricCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a metric collection is not found."""


class MetricCollectionRepository(TrunkEntityRepository[MetricCollection], abc.ABC):
    """A repository of metric collections."""
