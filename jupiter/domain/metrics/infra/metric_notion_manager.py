"""A manager of Notion-side metrics."""
from jupiter.domain.metrics.notion_metric import NotionMetric
from jupiter.domain.metrics.notion_metric_collection import NotionMetricCollection
from jupiter.domain.metrics.notion_metric_entry import NotionMetricEntry
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.notion_manager import (
    NotionBranchEntityNotFoundError,
    NotionLeafEntityNotFoundError,
    ParentTrunkBranchLeafNotionManager,
)


class NotionMetricNotFoundError(NotionBranchEntityNotFoundError):
    """Error raised when a Notion-side metric does not exist (but should)."""


class NotionMetricEntryNotFoundError(NotionLeafEntityNotFoundError):
    """Error raised when a Notion-side metric entry does not exist (but should)."""


class MetricNotionManager(
    ParentTrunkBranchLeafNotionManager[
        NotionWorkspace, NotionMetricCollection, NotionMetric, NotionMetricEntry, None
    ]
):
    """A manager of Notion-side metrics."""
