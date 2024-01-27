"""The command for reporting on progress."""
from typing import Final, Optional

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.report.report_breakdown import ReportBreakdown
from jupiter.core.domain.report.report_period_result import (
    ReportPeriodResult,
)
from jupiter.core.domain.report.service.report_service import ReportService
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInReadonlyUseCaseContext,
    readonly_use_case,
)
from jupiter.core.utils.time_provider import TimeProvider


@use_case_args
class ReportArgs(UseCaseArgsBase):
    """Report args."""

    today: Optional[ADate]
    period: RecurringTaskPeriod
    sources: Optional[list[InboxTaskSource]] = None
    breakdowns: list[ReportBreakdown] | None = None
    filter_project_ref_ids: Optional[list[EntityId]] = None
    filter_big_plan_ref_ids: Optional[list[EntityId]] = None
    filter_habit_ref_ids: Optional[list[EntityId]] = None
    filter_chore_ref_ids: Optional[list[EntityId]] = None
    filter_metric_ref_ids: Optional[list[EntityId]] = None
    filter_person_ref_ids: Optional[list[EntityId]] = None
    filter_slack_task_ref_ids: Optional[list[EntityId]] = None
    filter_email_task_ref_ids: Optional[list[EntityId]] = None
    breakdown_period: Optional[RecurringTaskPeriod] = None


@use_case_result
class ReportResult(UseCaseResultBase):
    """Report results."""

    period_result: ReportPeriodResult


@readonly_use_case()
class ReportUseCase(AppLoggedInReadonlyUseCase[ReportArgs, ReportResult]):
    """The command for reporting on progress."""

    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        time_provider: TimeProvider,
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
    ) -> None:
        super().__init__(auth_token_stamper, storage_engine)
        self._time_provider = time_provider

    async def _execute(
        self,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ReportArgs,
    ) -> ReportResult:
        """Execute the command."""
        user = context.user
        workspace = context.workspace

        report_service = ReportService(self._storage_engine, self._time_provider)

        report_period_result = await report_service.do_it(
            user=user,
            workspace=workspace,
            today=args.today,
            period=args.period,
            sources=args.sources,
            breakdowns=args.breakdowns,
            filter_project_ref_ids=args.filter_project_ref_ids,
            filter_big_plan_ref_ids=args.filter_big_plan_ref_ids,
            filter_habit_ref_ids=args.filter_habit_ref_ids,
            filter_chore_ref_ids=args.filter_chore_ref_ids,
            filter_metric_ref_ids=args.filter_metric_ref_ids,
            filter_person_ref_ids=args.filter_person_ref_ids,
            filter_slack_task_ref_ids=args.filter_slack_task_ref_ids,
            filter_email_task_ref_ids=args.filter_email_task_ref_ids,
            breakdown_period=args.breakdown_period,
        )

        return ReportResult(period_result=report_period_result)
