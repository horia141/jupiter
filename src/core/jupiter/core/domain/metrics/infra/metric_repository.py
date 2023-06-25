"""A repository of metrics."""
import abc

from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.framework.repository import (
    BranchEntityNotFoundError,
    BranchEntityRepository,
)


class MetricNotFoundError(BranchEntityNotFoundError):
    """Error raised when a metric does not exist."""


class MetricRepository(BranchEntityRepository[Metric], abc.ABC):
    """A repository of metrics."""
