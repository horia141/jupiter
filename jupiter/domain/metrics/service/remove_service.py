"""Shared service for removing a metric."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.metrics.infra.metric_notion_manager import (
    MetricNotionManager,
    NotionMetricNotFoundError,
)
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.storage_engine import DomainStorageEngine

LOGGER = logging.getLogger(__name__)


class MetricRemoveService:
    """Shared service for removing a metric."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        metric_notion_manager: MetricNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_notion_manager = metric_notion_manager

    def execute(self, metric_collection: MetricCollection, metric: Metric) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            for metric_entry in uow.metric_entry_repository.find_all(
                metric.ref_id, allow_archived=True
            ):
                uow.metric_entry_repository.remove(metric_entry.ref_id)

            uow.metric_repository.remove(metric.ref_id)

            workspace = uow.workspace_repository.load()
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )

            all_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_metric_ref_ids=[metric.ref_id],
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        for inbox_task in all_inbox_tasks:
            inbox_task_remove_service.do_it(inbox_task)

        # This needs to take into account notion entries too.
        try:
            self._metric_notion_manager.remove_branch(
                metric_collection.ref_id, metric.ref_id
            )
        except NotionMetricNotFoundError:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
