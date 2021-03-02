"""A repository of metrics."""
import abc
from typing import Optional, List, Iterable

from domain.metrics.metric import Metric
from models.basic import MetricKey, EntityId
from models.framework import Repository


class MetricRepository(Repository, abc.ABC):
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
    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Metric:
        """Find a metric by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> List[Metric]:
        """Find all metrics matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric - an irreversible operation."""
