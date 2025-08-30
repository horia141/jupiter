"""Stats about a journal."""

import abc

from jupiter.core.domain.application.report.report_period_result import (
    ReportPeriodResult,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.record import Record, create_record_action, record
from jupiter.core.framework.repository import RecordRepository


@record
class JournalStats(Record):
    """Stats about a journal."""

    journal: ParentLink
    report: ReportPeriodResult

    @staticmethod
    @create_record_action
    def new_stats(
        ctx: DomainContext,
        journal_ref_id: EntityId,
        today: ADate,
        period: RecurringTaskPeriod,
        sources: list[InboxTaskSource],
    ) -> "JournalStats":
        """Create a new journal stats."""
        return JournalStats._create(
            ctx,
            journal=ParentLink(journal_ref_id),
            report=ReportPeriodResult.empty(today, period, sources),
        )

    @staticmethod
    @create_record_action
    def new_stats_for_journal(
        ctx: DomainContext,
        journal_ref_id: EntityId,
        report: ReportPeriodResult,
    ) -> "JournalStats":
        """Create a new journal stats for a journal."""
        return JournalStats._create(
            ctx,
            journal=ParentLink(journal_ref_id),
            report=report,
        )

    @property
    def raw_key(self) -> object:
        """The raw key of the journal stats."""
        return self.journal.ref_id


class JournalStatsRepository(RecordRepository[JournalStats, EntityId], abc.ABC):
    """A repository of journal stats."""
