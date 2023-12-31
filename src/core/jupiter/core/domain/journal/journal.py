"""A journal for a particular time range."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.journal.journal_source import JournalSource
from jupiter.core.domain.report.report_period_result import ReportPeriodResult
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsAtMostOne,
    ContainsOne,
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)


@entity
class Journal(LeafEntity):
    """A journal for a particular range."""

    journal_collection_ref_id: ParentLink

    source: JournalSource
    right_now: ADate
    period: RecurringTaskPeriod
    timeline: str
    report: ReportPeriodResult

    note = OwnsOne(Note, domain=NoteDomain.JOURNAL, source_entity_ref_id=IsRefId())
    writing_task = OwnsAtMostOne(InboxTask, source=InboxTaskSource.JOURNAL, journal_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_journal_for_user(
        ctx: DomainContext,
        journal_collection_ref_id: EntityId,
        right_now: ADate,
        period: RecurringTaskPeriod,
    ) -> "Journal":
        """Create a journal."""
        return Journal._create(
            ctx,
            name=Journal.build_name(right_now, period),
            journal_collection_ref_id=ParentLink(journal_collection_ref_id),
            source=JournalSource.USER,
            right_now=right_now,
            period=period,
            timeline=infer_timeline(period, right_now.to_timestamp_at_end_of_day()),
            report=ReportPeriodResult.empty(right_now, period),
        )
    
    @staticmethod
    @create_entity_action
    def new_journal_for_period(
        ctx: DomainContext,
        journal_collection_ref_id: EntityId,
        right_now: ADate,
        period: RecurringTaskPeriod,
        timeline: str,
        report: ReportPeriodResult,
    ) -> "Journal":
        """Create a journal."""
        return Journal._create(
            ctx,
            name=Journal.build_name(right_now, period),
            journal_collection_ref_id=ParentLink(journal_collection_ref_id),
            source=JournalSource.RECURRING,
            right_now=right_now,
            period=period,
            timeline=timeline,
            report=report,
        )

    @update_entity_action
    def update_report(
        self,
        ctx: DomainContext,
        report: object,
    ) -> "Journal":
        """Update the report."""
        return self._new_version(ctx, report=report)

    @staticmethod
    def build_name(right_now: ADate, period: RecurringTaskPeriod) -> EntityName:
        """Build the name of the journal."""
        return EntityName(f"Journal {period}@{ADate.to_user_date_str(right_now)}")
