"""Use case for creating time plan actitivities for already existin activities."""
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
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
class TimePlanAssociateWithActivitiesArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    other_time_plan_ref_id: EntityId
    activity_ref_ids: list[EntityId]


@use_case_result
class TimePlanAssociateWithActivitiesResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanAssociateWithActivitiesUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimePlanAssociateWithActivitiesArgs, TimePlanAssociateWithActivitiesResult
    ]
):
    """Use case for creating activities starting from already existin activities."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanAssociateWithActivitiesArgs,
    ) -> TimePlanAssociateWithActivitiesResult:
        """Execute the command's actions."""
        _ = await uow.get_for(TimePlan).load_by_id(args.ref_id)

        activities = await uow.get_for(TimePlanActivity).find_all(
            parent_ref_id=args.other_time_plan_ref_id,
            allow_archived=False,
            filter_ref_ids=args.activity_ref_ids,
        )

        new_time_plan_actitivies = []

        for activity in activities:
            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity=activity,
            )
            new_time_plan_activity = await generic_creator(
                uow, progress_reporter, new_time_plan_activity
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

        return TimePlanAssociateWithActivitiesResult(
            new_time_plan_activities=new_time_plan_actitivies
        )
