"""A repository for metric collections."""
import abc

from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.framework.repository import TrunkEntityRepository, TrunkEntityNotFoundError


class MetricCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a metric collection is not found."""


class MetricCollectionRepository(TrunkEntityRepository[MetricCollection], abc.ABC):
    """A repository of metric collections."""
