"""Shared service for removing an inbox task."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.time_plans.time_plan_activity import (
    TimePlanActivityRespository,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class InboxTaskRemoveService:
    """Shared service for removing an inbox task."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        inbox_task: InboxTask,
    ) -> None:
        """Execute the service's action."""
        # Remove time plan activities that are associated with the inbox task.
        # These are entities that just represent the link between a time plan
        # and the inbox task. So they have to go!
        time_plan_activities = await uow.get(
            TimePlanActivityRespository
        ).find_all_generic(
            target=TimePlanActivityTarget.INBOX_TASK,
            target_ref_id=inbox_task.ref_id,
            allow_archived=True,
        )
        for time_plan_activity in time_plan_activities:
            await uow.get(TimePlanActivityRespository).remove(time_plan_activity.ref_id)

        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            ctx, uow, NoteDomain.INBOX_TASK, inbox_task.ref_id
        )
        await uow.get_for(InboxTask).remove(inbox_task.ref_id)
        await progress_reporter.mark_removed(inbox_task)
