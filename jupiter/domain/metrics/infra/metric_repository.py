"""A repository of metrics."""
import abc

from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.framework.repository import BranchEntityRepository, BranchEntityAlreadyExistsError,\
    BranchEntityNotFoundError


class MetricAlreadyExistsError(BranchEntityAlreadyExistsError):
    """Error raised when trying to create a metric and it already exists."""


class MetricNotFoundError(BranchEntityNotFoundError):
    """Error raised when a metric does not exist."""


class MetricRepository(BranchEntityRepository[MetricKey, Metric], abc.ABC):
    """A repository of metrics."""
