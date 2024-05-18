"""Use case for creating time plan actitivities for inbox tasks."""
from typing import cast
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity, TimePlanAlreadyAssociatedWithTarget
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class TimePlanAssociateWithInboxTasksArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    inbox_task_ref_id: list[EntityId]


@use_case_result
class TimePlanAssociateWithInboxTasksResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanAssociateWithInboxTasksUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimePlanAssociateWithInboxTasksArgs, TimePlanAssociateWithInboxTasksResult
    ]
):
    """Use case for creating activities starting from inbox tasks."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanAssociateWithInboxTasksArgs,
    ) -> TimePlanAssociateWithInboxTasksResult:
        """Execute the command's actions."""
        workspace = context.workspace

        _ = await uow.get_for(TimePlan).load_by_id(args.ref_id)

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(workspace.ref_id)
        inbox_tasks = await uow.get_for(InboxTask).find_all(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_ref_ids=args.inbox_task_ref_id
        )
        
        big_plan_ref_ids = [cast(EntityId, it.big_plan_ref_id) for it in inbox_tasks if it.source == InboxTaskSource.BIG_PLAN]
        big_plans = []
        if len(big_plan_ref_ids) > 0:
            big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(workspace.ref_id)
            big_plans = await uow.get_for(BigPlan).find_all(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=False,
                filter_ref_ids=big_plan_ref_ids
            )

        new_time_plan_actitivies = []

        for inbox_task in inbox_tasks:
            new_time_plan_activity = TimePlanActivity.new_activity_for_inbox_task(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                inbox_task_ref_id=inbox_task.ref_id,
                kind=TimePlanActivityKind.FINISH,
                feasability=TimePlanActivityFeasability.MUST_DO,
            )
            new_time_plan_activity = await generic_creator(
                uow, progress_reporter, new_time_plan_activity
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

        for big_plan in big_plans:
            try:
                new_time_plan_activity = TimePlanActivity.new_activity_for_big_plan(
                    context.domain_context,
                    time_plan_ref_id=args.ref_id,
                    big_plan_ref_id=big_plan.ref_id,
                    kind=TimePlanActivityKind.MAKE_PROGRESS,
                    feasability=TimePlanActivityFeasability.MUST_DO
                )
                new_time_plan_activity = await generic_creator(
                    uow, progress_reporter, new_time_plan_activity
                )
                new_time_plan_actitivies.append(new_time_plan_activity)
            except TimePlanAlreadyAssociatedWithTarget:
                # We were already working on this plan, no need to panic
                pass

        return TimePlanAssociateWithInboxTasksResult(
            new_time_plan_activities=new_time_plan_actitivies
        )
