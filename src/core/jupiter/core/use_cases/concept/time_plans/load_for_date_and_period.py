"""Retrieve details about a time plan."""

from jupiter.core.domain.concept.time_plans.time_plan import (
    TimePlan,
    TimePlanRepository,
)
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_name import EntityName
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
class TimePlanLoadForDateAndPeriodArgs(UseCaseArgsBase):
    """Args."""

    right_now: ADate
    period: RecurringTaskPeriod
    allow_archived: bool


@use_case_result
class TimePlanLoadForDateAndPeriodResult(UseCaseResultBase):
    """Result."""

    time_plan: TimePlan | None
    sub_period_time_plans: list[TimePlan]


@readonly_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanLoadForTimeDateAndPeriodUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        TimePlanLoadForDateAndPeriodArgs, TimePlanLoadForDateAndPeriodResult
    ]
):
    """The command for loading details about a time plan."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanLoadForDateAndPeriodArgs,
    ) -> TimePlanLoadForDateAndPeriodResult:
        """Execute the command's actions."""
        workspace = context.workspace
        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id
        )

        schedule = schedules.get_schedule(
            period=args.period,
            name=EntityName("Test"),
            right_now=args.right_now.to_timestamp_at_end_of_day(),
        )

        all_time_plans = await uow.get(TimePlanRepository).find_all_in_range(
            parent_ref_id=time_plan_domain.ref_id,
            allow_archived=False,
            filter_periods=[args.period, *args.period.all_smaller_periods],
            filter_start_date=schedule.first_day,
            filter_end_date=schedule.end_day,
        )

        return TimePlanLoadForDateAndPeriodResult(
            time_plan=next(
                (j for j in all_time_plans if j.period == args.period), None
            ),
            sub_period_time_plans=[
                tp for tp in all_time_plans if tp.period != args.period
            ],
        )
