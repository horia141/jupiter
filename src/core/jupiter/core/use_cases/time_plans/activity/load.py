"""Use case for loading a time plan activity activity."""
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan_activity_target import TimePlanActivityTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class TimePlanActivityLoadArgs(UseCaseArgsBase):
    """TimePlanActivityLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class TimePlanActivityLoadResult(UseCaseResultBase):
    """TimePlanActivityLoadResult."""

    time_plan_activity: TimePlanActivity
    target_inbox_task: InboxTask | None
    target_big_plan: BigPlan | None


@readonly_use_case(WorkspaceFeature.time_planS)
class TimePlanActivityLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        TimePlanActivityLoadArgs, TimePlanActivityLoadResult
    ]
):
    """Use case for loading a time plan activity activity."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanActivityLoadArgs,
    ) -> TimePlanActivityLoadResult:
        """Execute the command's action."""
        time_plan_activity, target_inbox_task, target_big_plan = await generic_loader(
            uow, 
            TimePlanActivity, 
            args.ref_id, 
            TimePlanActivity.target_inbox_task, 
            TimePlanActivity.target_big_plan,
            allow_archived=args.allow_archived
        )

        return TimePlanActivityLoadResult(time_plan_activity=time_plan_activity, 
                                          target_inbox_task=target_inbox_task,
                                          target_big_plan=target_big_plan)
