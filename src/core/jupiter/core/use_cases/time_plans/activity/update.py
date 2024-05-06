"""Update a time plan activity."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class TimePlanActivityUpdateArgs(UseCaseArgsBase):
    """TimePlanActivityFindArgs."""

    ref_id: EntityId
    kind: UpdateAction[TimePlanActivityKind]
    feasability: UpdateAction[TimePlanActivityFeasability]


@mutation_use_case(WorkspaceFeature.PERSONS)
class TimePlanActivityUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[TimePlanActivityUpdateArgs, None]
):
    """The command for updating a time plan activity."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanActivityUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        activity = await uow.get_for(TimePlanActivity).load_by_id(args.ref_id)
        activity = activity.update(
            context.domain_context, kind=args.kind, feasability=args.feasability
        )
        await uow.get_for(TimePlanActivity).save(activity)
        await progress_reporter.mark_updated(activity)
