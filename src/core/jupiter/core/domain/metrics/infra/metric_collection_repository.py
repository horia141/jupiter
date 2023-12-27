"""A repository for metric collections."""
import abc

from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class MetricCollectionRepository(TrunkEntityRepository[MetricCollection], abc.ABC):
    """A repository of metric collections."""
