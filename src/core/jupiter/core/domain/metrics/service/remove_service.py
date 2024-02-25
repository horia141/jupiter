"""Shared service for removing a metric."""

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class MetricRemoveService:
    """Shared service for removing a metric."""

    async def execute(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        metric: Metric,
    ) -> None:
        """Execute the command's action."""
        all_metric_entries = await uow.get_for(MetricEntry).find_all(
            metric.ref_id,
            allow_archived=True,
        )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )

        all_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            metric_ref_id=[metric.ref_id],
        )

        inbox_task_remove_service = InboxTaskRemoveService()
        for inbox_task in all_inbox_tasks:
            await inbox_task_remove_service.do_it(
                ctx, uow, progress_reporter, inbox_task
            )

        for metric_entry in all_metric_entries:
            await uow.get_for(MetricEntry).remove(metric_entry.ref_id)
            await progress_reporter.mark_removed(metric_entry)
            note_remove_service = NoteRemoveService()
            await note_remove_service.remove_for_source(
                ctx, uow, NoteDomain.METRIC_ENTRY, metric_entry.ref_id
            )

        await uow.get_for(Metric).remove(metric.ref_id)
        await progress_reporter.mark_removed(metric)
