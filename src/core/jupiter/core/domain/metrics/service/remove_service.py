"""Shared service for removing a metric."""

from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.use_case import ProgressReporter


class MetricRemoveService:
    """Shared service for removing a metric."""

    async def execute(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        metric: Metric,
    ) -> None:
        """Execute the command's action."""
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

        inbox_task_remove_service = InboxTaskRemoveService()
        for inbox_task in all_inbox_tasks:
            await inbox_task_remove_service.do_it(uow, progress_reporter, inbox_task)

        for metric_entry in all_metric_entries:
            await uow.metric_entry_repository.remove(metric_entry.ref_id)
            await progress_reporter.mark_removed(metric_entry)

        await uow.metric_repository.remove(metric.ref_id)
        await progress_reporter.mark_removed(metric)
