"""A repository of metrics."""
import abc
from typing import Optional, List, Iterable

from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class MetricAlreadyExistsError(Exception):
    """Error raised when trying to create a metric and it already exists."""


class MetricNotFoundError(Exception):
    """Error raised when a metric does not exist."""


class MetricRepository(Repository, abc.ABC):
    """A repository of metrics."""

    @abc.abstractmethod
    def create(self, metric: Metric) -> Metric:
        """Create a metric."""

    @abc.abstractmethod
    def save(self, metric: Metric) -> Metric:
        """Save a metric - it should already exist."""

    @abc.abstractmethod
    def load_by_key(self, key: MetricKey) -> Metric:
        """Find a metric by key."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Metric:
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
