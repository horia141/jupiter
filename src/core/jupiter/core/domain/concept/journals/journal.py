"""A journal for a particular time range."""

import abc

from jupiter.core.domain.application.report.report_period_result import (
    ReportPeriodResult,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.journals.journal_source import JournalSource
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    LeafEntityRepository,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class Journal(LeafEntity):
    """A journal for a particular range."""

    journal_collection: ParentLink

    source: JournalSource
    right_now: ADate
    period: RecurringTaskPeriod
    timeline: str
    report: ReportPeriodResult

    note = OwnsOne(Note, domain=NoteDomain.JOURNAL, source_entity_ref_id=IsRefId())
    writing_task = OwnsAtMostOne(
        InboxTask, source=InboxTaskSource.JOURNAL, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_journal_for_user(
        ctx: DomainContext,
        journal_collection_ref_id: EntityId,
        right_now: ADate,
        period: RecurringTaskPeriod,
        sources: list[InboxTaskSource],
    ) -> "Journal":
        """Create a journal."""
        return Journal._create(
            ctx,
            name=Journal.build_name(right_now, period),
            journal_collection=ParentLink(journal_collection_ref_id),
            source=JournalSource.USER,
            right_now=right_now,
            period=period,
            timeline=infer_timeline(period, right_now.to_timestamp_at_end_of_day()),
            report=ReportPeriodResult.empty(right_now, period, sources),
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
            journal_collection=ParentLink(journal_collection_ref_id),
            source=JournalSource.RECURRING,
            right_now=right_now,
            period=period,
            timeline=timeline,
            report=report,
        )

    @update_entity_action
    def change_time_config(
        self,
        ctx: DomainContext,
        right_now: UpdateAction[ADate],
        period: UpdateAction[RecurringTaskPeriod],
    ) -> "Journal":
        """Update the journal."""
        return self._new_version(
            ctx,
            name=Journal.build_name(
                right_now.or_else(self.right_now), period.or_else(self.period)
            ),
            right_now=right_now.or_else(self.right_now),
            period=period.or_else(self.period),
            timeline=infer_timeline(
                period.or_else(self.period),
                right_now.or_else(self.right_now).to_timestamp_at_end_of_day(),
            ),
        )

    @update_entity_action
    def update_report(
        self,
        ctx: DomainContext,
        report: ReportPeriodResult,
    ) -> "Journal":
        """Update the report."""
        return self._new_version(ctx, report=report)

    @staticmethod
    def build_name(right_now: ADate, period: RecurringTaskPeriod) -> EntityName:
        """Build the name of the journal."""
        return EntityName(f"{period.value.capitalize()} journal for {right_now}")


class JournalExistsForDatePeriodCombinationError(EntityAlreadyExistsError):
    """An error raised when a journal already exists for a date and period combination."""


class JournalRepository(LeafEntityRepository[Journal], abc.ABC):
    """The repository for journals."""

    @abc.abstractmethod
    async def find_all_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_periods: list[RecurringTaskPeriod],
        filter_start_date: ADate,
        filter_end_date: ADate,
    ) -> list[Journal]:
        """Find all journals in a range."""
