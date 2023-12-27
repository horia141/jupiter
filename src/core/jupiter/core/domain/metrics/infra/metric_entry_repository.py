"""A repository of metric entries."""
import abc

from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class MetricEntryRepository(LeafEntityRepository[MetricEntry], abc.ABC):
    """A repository of metric entries."""
