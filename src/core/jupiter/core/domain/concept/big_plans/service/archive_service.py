"""Shared logic for archiving a big plan."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.value import CompositeValue, value


@value
class BigPlanArchiveServiceResult(CompositeValue):
    """The result of the archive operation."""

    archived_inbox_tasks: list[InboxTask]


class BigPlanArchiveService:
    """Shared logic for archiving a big plan."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        big_plan: BigPlan,
        archival_reason: ArchivalReason,
    ) -> BigPlanArchiveServiceResult:
        """Execute the service's action."""
        if big_plan.archived:
            return BigPlanArchiveServiceResult(archived_inbox_tasks=[])

        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_id(
            big_plan.big_plan_collection.ref_id,
        )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            big_plan_collection.workspace.ref_id,
        )
        inbox_tasks_to_archive = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            source_entity_ref_id=big_plan.ref_id,
            source=InboxTaskSource.BIG_PLAN,
            allow_archived=True,
        )

        archived_inbox_tasks = []

        inbox_task_archive_service = InboxTaskArchiveService()
        for inbox_task in inbox_tasks_to_archive:
            if inbox_task.archived:
                continue
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task, archival_reason
            )
            archived_inbox_tasks.append(inbox_task)

        note_archive_service = NoteArchiveService()
        await note_archive_service.archive_for_source(
            ctx, uow, NoteDomain.BIG_PLAN, big_plan.ref_id, archival_reason
        )

        big_plan = big_plan.mark_archived(ctx, archival_reason)
        await uow.get_for(BigPlan).save(big_plan)
        await progress_reporter.mark_updated(big_plan)

        return BigPlanArchiveServiceResult(archived_inbox_tasks=archived_inbox_tasks)
