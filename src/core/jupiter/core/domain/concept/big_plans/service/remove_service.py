"""Shared module for removing a big plan."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class BigPlanRemoveService:
    """Shared service for removing a big plan."""

    async def remove(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        reporter: ProgressReporter,
        workspace: Workspace,
        ref_id: EntityId,
    ) -> None:
        """Hard remove a big plan."""
        big_plan = await uow.get_for(BigPlan).load_by_id(
            ref_id,
            allow_archived=True,
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_tasks_to_remove = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            big_plan_ref_ids=[ref_id],
        )

        for inbox_task in inbox_tasks_to_remove:
            await uow.get_for(InboxTask).remove(inbox_task.ref_id)
            await reporter.mark_removed(inbox_task)

        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            ctx, uow, NoteDomain.BIG_PLAN, big_plan.ref_id
        )

        big_plan = await uow.get_for(BigPlan).remove(ref_id)
        await reporter.mark_removed(big_plan)
