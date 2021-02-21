"""A repository of metrics."""
import abc
from typing import Optional, List, Iterable

from domain.metrics.metric import Metric
from models.basic import MetricKey


class MetricRepository(abc.ABC):
    """A repository of metrics."""

    @abc.abstractmethod
    def create(self, metric: Metric) -> Metric:
        """Create a metric."""

    @abc.abstractmethod
    def save(self, metric: Metric) -> Metric:
        """Save a metric - it should already exist."""

    @abc.abstractmethod
    def get_by_key(self, key: MetricKey) -> Metric:
        """Find a metric by key."""

    @abc.abstractmethod
    def find_all(self, allow_archived: bool, filter_keys: Optional[Iterable[MetricKey]]) -> List[Metric]:
        """Find all metrics matching some criteria."""

    @abc.abstractmethod
    def remove(self, metric: Metric) -> None:
        """Hard remove a metric - an irreversible operation."""
