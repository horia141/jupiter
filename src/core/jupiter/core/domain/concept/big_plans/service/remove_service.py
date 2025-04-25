"""Shared module for removing a big plan."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_stats import BigPlanStatsRepository
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.time_plans.time_plan_activity import (
    TimePlanActivityRespository,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
        inbox_tasks_to_remove = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.BIG_PLAN,
            source_entity_ref_id=ref_id,
        )

        if len(inbox_tasks_to_remove) > 0:
            time_plan_activities_for_inbox_tasks = await uow.get(
                TimePlanActivityRespository
            ).find_all_generic(
                target=TimePlanActivityTarget.INBOX_TASK,
                target_ref_id=[it.ref_id for it in inbox_tasks_to_remove],
                allow_archived=True,
            )
            for time_plan_activity in time_plan_activities_for_inbox_tasks:
                await uow.get(TimePlanActivityRespository).remove(
                    time_plan_activity.ref_id
                )

        for inbox_task in inbox_tasks_to_remove:
            await uow.get_for(InboxTask).remove(inbox_task.ref_id)
            await reporter.mark_removed(inbox_task)

        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            ctx, uow, NoteDomain.BIG_PLAN, big_plan.ref_id
        )

        time_plan_activities_for_big_plan = await uow.get(
            TimePlanActivityRespository
        ).find_all_generic(
            target=TimePlanActivityTarget.BIG_PLAN,
            target_ref_id=big_plan.ref_id,
            allow_archived=True,
        )
        for time_plan_activity in time_plan_activities_for_big_plan:
            await uow.get(TimePlanActivityRespository).remove(time_plan_activity.ref_id)

        await uow.get(BigPlanStatsRepository).remove(big_plan.ref_id)

        big_plan = await uow.get_for(BigPlan).remove(ref_id)
        await reporter.mark_removed(big_plan)
