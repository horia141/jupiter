"""A repository of metrics."""
import abc

from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.framework.repository import (
    BranchEntityRepository,
)


class MetricRepository(BranchEntityRepository[Metric], abc.ABC):
    """A repository of metrics."""
