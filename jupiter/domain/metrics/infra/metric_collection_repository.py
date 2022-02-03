"""A repository for metric collections."""
import abc

from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class MetricCollectionNotFoundError(Exception):
    """Error raised when a metric collection is not found."""


class MetricCollectionRepository(Repository, abc.ABC):
    """A repository of metric collections."""

    @abc.abstractmethod
    def create(self, metric_collection: MetricCollection) -> MetricCollection:
        """Create a metric collection."""

    @abc.abstractmethod
    def save(self, metric_collection: MetricCollection) -> MetricCollection:
        """Save a metric collection."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> MetricCollection:
        """Retrieve a metric collection by its owning workspace id."""
