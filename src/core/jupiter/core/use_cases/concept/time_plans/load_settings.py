"""Use case for loading the settings around time plans."""

from jupiter.core.domain.app import AppCore
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.concept.time_plans.time_plan_generation_approach import TimePlanGenerationApproach
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class TimePlanLoadSettingsArgs(UseCaseArgsBase):
    """TimePlanLoadSettingsArgs."""


@use_case_result
class TimePlanLoadSettingsResult(UseCaseResultBase):
    """TimePlanLoadSettingsResult."""

    periods: list[RecurringTaskPeriod]
    generation_approach: TimePlanGenerationApproach
    generation_in_advance_days: dict[RecurringTaskPeriod, int]
    planning_task_project: Project | None
    planning_task_gen_params: RecurringTaskGenParams | None


@readonly_use_case(WorkspaceFeature.TIME_PLANS, exclude_app=[AppCore.CLI])
class TimePlanLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        TimePlanLoadSettingsArgs, TimePlanLoadSettingsResult
    ],
):
    """The command for loading the settings around journals."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanLoadSettingsArgs,
    ) -> TimePlanLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id,
        )

        if time_plan_domain.planning_task_project_ref_id is not None:
            planning_task_project = await uow.get_for(Project).load_by_id(
                time_plan_domain.planning_task_project_ref_id,
            )
        else:
            planning_task_project = None


        return TimePlanLoadSettingsResult(
            periods=list(time_plan_domain.periods),
            generation_approach=time_plan_domain.generation_approach,
            generation_in_advance_days=time_plan_domain.generation_in_advance_days,
            planning_task_project=planning_task_project,
            planning_task_gen_params=time_plan_domain.planning_task_gen_params,
        )
