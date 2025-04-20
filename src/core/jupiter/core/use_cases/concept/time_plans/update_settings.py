"""Update settings around time plans."""

from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.concept.time_plans.time_plan_generation_approach import (
    TimePlanGenerationApproach,
)
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class TimePlanUpdateSettingsArgs(UseCaseArgsBase):
    """Args."""

    periods: UpdateAction[list[RecurringTaskPeriod]]
    generation_approach: UpdateAction[TimePlanGenerationApproach]
    generation_in_advance_days: UpdateAction[dict[RecurringTaskPeriod, int]]
    planning_task_project_ref_id: UpdateAction[EntityId | None]
    planning_task_eisen: UpdateAction[Eisen | None]
    planning_task_difficulty: UpdateAction[Difficulty | None]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanUpdateSettingsUseCase(
    AppTransactionalLoggedInMutationUseCase[TimePlanUpdateSettingsArgs, None]
):
    """Command for updating the settings for time plans in general."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanUpdateSettingsArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id
        )

        if args.periods.should_change:
            # Process all auto-generated time plans
            pass

        if args.planning_task_project_ref_id.should_change:
            if args.planning_task_project_ref_id.just_the_value is not None:
                _ = await uow.get_for(Project).load_by_id(
                    args.planning_task_project_ref_id.just_the_value
                )

        if (
            args.planning_task_eisen.should_change
            or args.planning_task_difficulty.should_change
        ):
            # Process all auto-generated tasks
            pass

        time_plan_domain = time_plan_domain.update(
            context.domain_context,
            periods=args.periods.transform(lambda s: set(s)),
            generation_approach=args.generation_approach,
            generation_in_advance_days=args.generation_in_advance_days,
            planning_task_project_ref_id=args.planning_task_project_ref_id,
            planning_task_eisen=args.planning_task_eisen,
            planning_task_difficulty=args.planning_task_difficulty,
        )
        await uow.get_for(TimePlanDomain).save(time_plan_domain)
