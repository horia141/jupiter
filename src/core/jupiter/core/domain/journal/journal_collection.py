"""A journal attached to a workspace."""
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
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
    writing_task_project_ref_id: EntityId
    writing_task_gen_params: RecurringTaskGenParams

    entries = ContainsMany(Journal, journal_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_journal_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        periods: set[RecurringTaskPeriod],
        writing_project_ref_id: EntityId,
        writing_task_eisen: Eisen,
        writing_task_difficulty: Difficulty,
    ) -> "JournalCollection":
        """Create a journal."""
        JournalCollection._check_periods_are_safe(periods)
        return JournalCollection._create(
            ctx, workspace=ParentLink(workspace_ref_id), 
            periods=periods,
            writing_project_ref_id=writing_project_ref_id,
            writing_gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=writing_task_eisen,
                difficulty=writing_task_difficulty,
            ),
        )

    @update_entity_action
    def change_periods(
        self,
        ctx: DomainContext,
        periods: set[RecurringTaskPeriod],
    ) -> "JournalCollection":
        """Update the journal."""
        JournalCollection._check_periods_are_safe(periods)
        return self._new_version(ctx, periods=periods)
    
    @update_entity_action
    def change_writing_tasks(
        self,
        ctx: DomainContext,
        writing_task_project_ref_id: UpdateAction[EntityId],
        writing_task_eisen: UpdateAction[Eisen],
        writing_task_difficulty: UpdateAction[Difficulty],
    ) -> "JournalCollection":
        """Change the writing project."""
        return self._new_version(
            ctx,
            writing_task_project_ref_id=writing_task_project_ref_id.or_else(self.writing_task_project_ref_id),
            writing_task_gen_params=RecurringTaskGenParams(
                period=self.writing_task_gen_params.period,
                eisen=writing_task_eisen.or_else(self.writing_task_gen_params.eisen or Eisen.REGULAR),
                difficulty=writing_task_difficulty.or_else(self.writing_task_gen_params.difficulty or Difficulty.EASY),
            ) if writing_task_eisen.should_change or writing_task_difficulty.should_change else self.writing_task_gen_params,
        )

    @staticmethod
    def _check_periods_are_safe(periods: set[RecurringTaskPeriod]) -> None:
        if len(periods) == 0:
            raise InputValidationError("The periods cannot be empty.")
