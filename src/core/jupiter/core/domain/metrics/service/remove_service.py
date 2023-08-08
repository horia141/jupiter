"""Shared service for removing a metric."""
from typing import Final

from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.use_case import ProgressReporter


class MetricRemoveService:
    """Shared service for removing a metric."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def execute(
        self,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        metric_collection: MetricCollection,
        metric: Metric,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            all_metric_entries = await uow.metric_entry_repository.find_all(
                metric.ref_id,
                allow_archived=True,
            )

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )

            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_metric_ref_ids=[metric.ref_id],
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine,
        )
        for inbox_task in all_inbox_tasks:
            await inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        async with self._storage_engine.get_unit_of_work() as uow:
            for metric_entry in all_metric_entries:
                await uow.metric_entry_repository.remove(metric_entry.ref_id)
                await progress_reporter.mark_removed(metric_entry)

            await uow.metric_repository.remove(metric.ref_id)
            await progress_reporter.mark_removed(metric)
