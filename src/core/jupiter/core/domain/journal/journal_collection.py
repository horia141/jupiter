"""A journal attached to a workspace."""
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.journal.journal import Journal
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction


@entity
class JournalCollection(TrunkEntity):
    """A journal."""

    workspace: ParentLink

    periods: set[RecurringTaskPeriod]

    entries = ContainsMany(Journal, journal_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_journal_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        periods: set[RecurringTaskPeriod],
    ) -> "JournalCollection":
        """Create a journal."""
        JournalCollection._check_periods_are_safe(periods)
        return JournalCollection._create(
            ctx, workspace=ParentLink(workspace_ref_id), periods=periods
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        periods: UpdateAction[set[RecurringTaskPeriod]],
    ) -> "JournalCollection":
        """Update the journal."""
        JournalCollection._check_periods_are_safe(periods.or_else(self.periods))
        return self._new_version(ctx, periods=periods.or_else(self.periods))

    @staticmethod
    def _check_periods_are_safe(periods: set[RecurringTaskPeriod]) -> None:
        if len(periods) == 0:
            raise InputValidationError("The periods cannot be empty.")
