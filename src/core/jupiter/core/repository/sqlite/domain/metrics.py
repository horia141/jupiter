"""SQLite based metrics repositories."""

from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import (
    MetricRepository,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteBranchEntityRepository,
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)


class SqliteMetricCollectionRepository(
    SqliteTrunkEntityRepository[MetricCollection], MetricCollectionRepository
):
    """The metric collection repository."""


class SqliteMetricRepository(SqliteBranchEntityRepository[Metric], MetricRepository):
    """A repository for metrics."""


class SqliteMetricEntryRepository(
    SqliteLeafEntityRepository[MetricEntry], MetricEntryRepository
):
    """A repository of metric entries."""
