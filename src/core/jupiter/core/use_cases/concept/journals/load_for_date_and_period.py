"""Retrieve details about a journal."""
from jupiter.core.domain.concept.journals.journal import Journal, JournalRepository
from jupiter.core.domain.concept.journals.journal_collection import JournalCollection
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
class JournalLoadForDateAndPeriodArgs(UseCaseArgsBase):
    """Args."""

    right_now: ADate
    period: RecurringTaskPeriod
    allow_archived: bool


@use_case_result
class JournalLoadForDateAndPeriodResult(UseCaseResultBase):
    """Result."""

    journal: Journal | None
    sub_period_journals: list[Journal]


@readonly_use_case(WorkspaceFeature.JOURNALS)
class JournalLoadForDateAndPeriodUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        JournalLoadForDateAndPeriodArgs, JournalLoadForDateAndPeriodResult
    ]
):
    """The command for loading details about a journal."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: JournalLoadForDateAndPeriodArgs,
    ) -> JournalLoadForDateAndPeriodResult:
        """Execute the command's actions."""
        workspace = context.workspace
        journal_collection = await uow.get_for(JournalCollection).load_by_parent(
            workspace.ref_id
        )
        schedule = schedules.get_schedule(
            period=args.period,
            name=EntityName("Test"),
            right_now=args.right_now.to_timestamp_at_end_of_day(),
        )

        all_journals = await uow.get(JournalRepository).find_all_in_range(
            parent_ref_id=journal_collection.ref_id,
            allow_archived=False,
            filter_periods=[args.period, *args.period.all_smaller_periods],
            filter_start_date=schedule.first_day,
            filter_end_date=schedule.end_day,
        )

        return JournalLoadForDateAndPeriodResult(
            journal=next((j for j in all_journals if j.period == args.period), None),
            sub_period_journals=[j for j in all_journals if j.period != args.period],
        )
