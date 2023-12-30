"""A journal for a particular time range."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsOne,
    IsRefId,
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)


@entity
class Journal(LeafEntity):
    """A journal for a particular range."""

    journal_collection_ref_id: ParentLink

    right_now: ADate
    period: RecurringTaskPeriod
    timeline: str
    report: object  # TODO: Add report type

    note = ContainsOne(Note, domain=NoteDomain.JOURNAL, source_entity_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_journal(
        ctx: DomainContext,
        journal_collection_ref_id: EntityId,
        right_now: ADate,
        period: RecurringTaskPeriod,
        timeline: str,
        report: object,
    ) -> "Journal":
        """Create a journal."""
        return Journal._create(
            ctx,
            name=Journal.build_name(right_now, period),
            journal_collection_ref_id=ParentLink(journal_collection_ref_id),
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
