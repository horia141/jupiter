"""Use case for loading the settings around time plans."""

from jupiter.core.domain.app import AppCore
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase, use_case_args, use_case_result
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext, AppTransactionalLoggedInReadOnlyUseCase, readonly_use_case


@use_case_args
class TimePlanLoadSettingsArgs(UseCaseArgsBase):
    """TimePlanLoadSettingsArgs."""


@use_case_result
class TimePlanLoadSettingsResult(UseCaseResultBase):
    """TimePlanLoadSettingsResult."""

    periods: list[RecurringTaskPeriod]
    planning_task_project: Project
    planning_task_gen_params: RecurringTaskGenParams


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
        planning_task_project = await uow.get_for(Project).load_by_id(
            time_plan_domain.planning_task_project_ref_id,
        )

        return TimePlanLoadSettingsResult(
            periods=list(time_plan_domain.periods),
            planning_task_project=planning_task_project,
            planning_task_gen_params=time_plan_domain.planning_task_gen_params,
        )
