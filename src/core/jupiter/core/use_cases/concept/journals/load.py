"""Retrieve details about a journal."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.journals.journal import Journal, JournalRepository
from jupiter.core.domain.concept.journals.journal_stats import (
    JournalStats,
    JournalStatsRepository,
)
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class JournalLoadArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class JournalLoadResult(UseCaseResultBase):
    """Result."""

    journal: Journal
    note: Note
    journal_stats: JournalStats
    writing_task: InboxTask | None
    sub_period_journals: list[Journal]


@readonly_use_case(WorkspaceFeature.JOURNALS)
class JournalLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[JournalLoadArgs, JournalLoadResult]
):
    """The command for loading details about a journal."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: JournalLoadArgs,
    ) -> JournalLoadResult:
        """Execute the command's actions."""
        journal, note, writing_task = await generic_loader(
            uow,
            Journal,
            args.ref_id,
            Journal.note,
            Journal.writing_task,
            allow_archived=args.allow_archived,
            allow_subentity_archived=True,
        )

        journal_stats = await uow.get(JournalStatsRepository).load_by_key_optional(
            journal.ref_id
        )

        if journal_stats is None:
            raise Exception("Journal stats not found")

        schedule = schedules.get_schedule(
            period=journal.period,
            name=journal.name,
            right_now=journal.right_now.to_timestamp_at_end_of_day(),
        )

        sub_period_journals = await uow.get(JournalRepository).find_all_in_range(
            parent_ref_id=journal.journal_collection.ref_id,
            allow_archived=False,
            filter_periods=journal.period.all_smaller_periods,
            filter_start_date=schedule.first_day,
            filter_end_date=schedule.end_day,
        )

        return JournalLoadResult(
            journal=journal,
            note=note,
            journal_stats=journal_stats,
            writing_task=writing_task,
            sub_period_journals=sub_period_journals,
        )
