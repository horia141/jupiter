"""The service class for syncing the METRIC database between local and Notion."""
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.notion_metric import NotionMetric
from jupiter.domain.metrics.notion_metric_collection import NotionMetricCollection
from jupiter.domain.metrics.notion_metric_entry import NotionMetricEntry
from jupiter.domain.notion_sync_service import TrunkBranchLeafNotionSyncService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class MetricSyncService(
    TrunkBranchLeafNotionSyncService[
        MetricCollection,
        Metric,
        MetricEntry,
        NotionWorkspace,
        NotionMetricCollection,
        NotionMetric,
        NotionMetricEntry,
        None,
        None,
        None,
    ]
):
    """The service class for syncing the metrics database between local and Notion."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        metric_notion_manager: MetricNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            MetricCollection,
            Metric,
            MetricEntry,
            NotionMetric,
            NotionMetricEntry,
            storage_engine,
            metric_notion_manager,
        )
