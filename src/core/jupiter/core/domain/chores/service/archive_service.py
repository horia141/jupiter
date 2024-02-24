"""Shared service for archiving a chore."""

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class ChoreArchiveService:
    """Shared service for archiving a chore."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        chore: Chore,
    ) -> None:
        """Execute the service's action."""
        if chore.archived:
            return

        chore_collection = await uow.repository_for(ChoreCollection).load_by_id(
            chore.chore_collection.ref_id,
        )
        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(
                chore_collection.workspace.ref_id,
            )
        )
        inbox_tasks_to_archive = await uow.repository_for(InboxTask).find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_chore_ref_ids=[chore.ref_id],
        )

        inbox_task_archive_service = InboxTaskArchiveService()

        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task
            )

        chore = chore.mark_archived(ctx)
        await uow.repository_for(Chore).save(chore)
        await progress_reporter.mark_updated(chore)
