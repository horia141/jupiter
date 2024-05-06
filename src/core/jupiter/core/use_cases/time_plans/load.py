"""Retrieve details about a time plan."""
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan, TimePlanRepository
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
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
class TimePlanLoadArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class TimePlanLoadResult(UseCaseResultBase):
    """Result."""

    time_plan: TimePlan
    note: Note
    activities: list[TimePlanActivity]
    sub_period_time_plans: list[TimePlan]


@readonly_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[TimePlanLoadArgs, TimePlanLoadResult]
):
    """The command for loading details about a time plan."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanLoadArgs,
    ) -> TimePlanLoadResult:
        """Execute the command's actions."""
        time_plan, activities, note = await generic_loader(
            uow,
            TimePlan,
            args.ref_id,
            TimePlan.activities,
            TimePlan.note,
            allow_archived=args.allow_archived,
        )

        schedule = schedules.get_schedule(
            period=time_plan.period,
            name=time_plan.name,
            right_now=time_plan.right_now.to_timestamp_at_end_of_day(),
        )

        sub_period_time_plans = await uow.get(TimePlanRepository).find_all_in_range(
            parent_ref_id=time_plan.time_plan_domain.ref_id,
            allow_archived=args.allow_archived,
            filter_periods=time_plan.period.all_smaller_periods,
            filter_start_date=schedule.first_day,
            filter_end_date=schedule.end_day,
        )

        return TimePlanLoadResult(
            time_plan=time_plan,
            activities=list(activities),
            note=note,
            sub_period_time_plans=sub_period_time_plans,
        )
