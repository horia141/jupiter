"""A journal attached to a workspace."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.journals.journal import Journal
from jupiter.core.domain.concept.journals.journal_generation_approach import JournalGenerationApproach
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
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
    generation_approach: JournalGenerationApproach
    generation_in_advance_days: dict[RecurringTaskPeriod, int]
    writing_task_project_ref_id: EntityId
    writing_task_gen_params: RecurringTaskGenParams | None

    entries = ContainsMany(Journal, journal_collection_ref_id=IsRefId())
    writing_tasks = ContainsMany(InboxTask, source=InboxTaskSource.JOURNAL)

    @staticmethod
    @create_entity_action
    def new_journal_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        periods: set[RecurringTaskPeriod],
        generation_approach: JournalGenerationApproach,
        generation_in_advance_days: dict[RecurringTaskPeriod, int],
        writing_task_project_ref_id: EntityId,
        writing_task_eisen: Eisen | None,
        writing_task_difficulty: Difficulty | None,
    ) -> "JournalCollection":
        """Create a journal."""
        final_generation_in_advance_days: dict[RecurringTaskPeriod, int]
        if generation_approach == JournalGenerationApproach.NONE:
            if len(generation_in_advance_days) > 0:
                raise InputValidationError(
                    "Generation in advance days cannot be set if generation approach is NONE"
                )
            if writing_task_eisen is not None:
                raise InputValidationError(
                    "Writing task eisen cannot be set if generation approach is NONE"
                )
            if writing_task_difficulty is not None:
                raise InputValidationError(
                    "Writing task difficulty cannot be set if generation approach is NONE"
                )
            final_generation_in_advance_days = {}
            final_writing_task_gen_params = None
        elif generation_approach == JournalGenerationApproach.ONLY_JOURNAL:
            if periods != generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is ONLY_JOURNAL"
                )
            if writing_task_eisen is not None:
                raise InputValidationError(
                    "Writing task eisen cannot be set if generation approach is NONE"
                )
            if writing_task_difficulty is not None:
                raise InputValidationError(
                    "Writing task difficulty cannot be set if generation approach is NONE"
                )
            final_generation_in_advance_days = {}
            final_writing_task_gen_params = None
        elif generation_approach == JournalGenerationApproach.BOTH_JOURNAL_AND_TASK:
            if periods != generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is BOTH_JOURNAL_AND_TASK"
                )
            if writing_task_eisen is None:
                raise InputValidationError(
                    "Writing task eisen must be set if generation approach is ONLY_TASK"
                )
            if writing_task_difficulty is None:
                raise InputValidationError(
                    "Writing task difficulty must be set if generation approach is BOTH_JOURNAL_AND_TASK"
                )
            final_generation_in_advance_days = generation_in_advance_days
            final_writing_task_gen_params = RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=writing_task_eisen,
                difficulty=writing_task_difficulty,
                actionable_from_day=None,
                actionable_from_month=None,
                due_at_day=None,
                due_at_month=None,
                skip_rule=None,
            )
        JournalCollection._validate_generation_in_advance_days(
            final_generation_in_advance_days
        )
        return JournalCollection._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=final_generation_in_advance_days,
            writing_task_project_ref_id=writing_task_project_ref_id,
            writing_task_gen_params=final_writing_task_gen_params,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        periods: UpdateAction[set[RecurringTaskPeriod]],
        generation_approach: UpdateAction[JournalGenerationApproach],
        generation_in_advance_days: UpdateAction[dict[RecurringTaskPeriod, int]],
        writing_task_project_ref_id: UpdateAction[EntityId],
        writing_task_eisen: UpdateAction[Eisen | None],
        writing_task_difficulty: UpdateAction[Difficulty | None],
    ) -> "JournalCollection":
        """Update the journal collection."""
        final_periods = periods.or_else(self.periods)
        final_generation_approach = generation_approach.or_else(
            self.generation_approach
        )
        final_generation_in_advance_days = generation_in_advance_days.or_else(
            self.generation_in_advance_days
        )
        final_writing_task_project_ref_id = writing_task_project_ref_id.or_else(
            self.writing_task_project_ref_id
        )
        final_writing_task_eisen = writing_task_eisen.or_else(
            self.writing_task_gen_params.eisen
            if self.writing_task_gen_params is not None
            else None
        )
        final_writing_task_difficulty = writing_task_difficulty.or_else(
            self.writing_task_gen_params.difficulty
            if self.writing_task_gen_params is not None
            else None
        )

        if final_generation_approach == JournalGenerationApproach.NONE:
            if len(final_generation_in_advance_days) > 0:
                raise InputValidationError(
                    "Generation in advance days cannot be set if generation approach is NONE"
                )
            if final_writing_task_eisen is not None:
                raise InputValidationError(
                    "Writing task eisen cannot be set if generation approach is NONE"
                )
            if final_writing_task_difficulty is not None:
                raise InputValidationError(
                    "Writing task difficulty cannot be set if generation approach is NONE"
                )
            final_writing_task_gen_params = None
        elif final_generation_approach == JournalGenerationApproach.ONLY_JOURNAL:
            if final_periods != final_generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is ONLY_JOURNAL"
                )
            if final_writing_task_eisen is not None:
                raise InputValidationError(
                    "Writing task eisen cannot be set if generation approach is NONE"
                )
            if final_writing_task_difficulty is not None:
                raise InputValidationError(
                    "Writing task difficulty cannot be set if generation approach is NONE"
                )
            final_writing_task_gen_params = None
        elif final_generation_approach == JournalGenerationApproach.BOTH_JOURNAL_AND_TASK:
            if final_periods != final_generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is BOTH_JOURNAL_AND_TASK"
                )
            if final_writing_task_eisen is None:
                raise InputValidationError(
                    "Writing task eisen must be set if generation approach is ONLY_TASK"
                )
            if final_writing_task_difficulty is None:
                raise InputValidationError(
                    "Writing task difficulty must be set if generation approach is BOTH_JOURNAL_AND_TASK"
                )
            final_writing_task_gen_params = RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=final_writing_task_eisen,
                difficulty=final_writing_task_difficulty,
                actionable_from_day=None,
                actionable_from_month=None,
                due_at_day=None,
                due_at_month=None,
                skip_rule=None,
            )
        JournalCollection._validate_generation_in_advance_days(
            final_generation_in_advance_days
        )

        return self._new_version(
            ctx,
            periods=final_periods,
            generation_approach=final_generation_approach,
            generation_in_advance_days=final_generation_in_advance_days,
            writing_task_project_ref_id=final_writing_task_project_ref_id,
            writing_task_gen_params=final_writing_task_gen_params,
        )

    @update_entity_action
    def change_writing_task_project_if_required(
        self,
        ctx: DomainContext,
        writing_task_project_ref_id: EntityId,
    ) -> "JournalCollection":
        """Change the writing task project."""
        return self._new_version(
            ctx,
            writing_task_project_ref_id=writing_task_project_ref_id,
        )

    @staticmethod
    def _validate_generation_in_advance_days(
        generation_in_advance_days: dict[RecurringTaskPeriod, int],
    ) -> None:
        """Validate the generation in advance days."""
        if RecurringTaskPeriod.DAILY in generation_in_advance_days:
            if generation_in_advance_days[RecurringTaskPeriod.DAILY] != 1:
                raise InputValidationError(
                    "Generation in advance days for daily must be 1"
                )
        if RecurringTaskPeriod.WEEKLY in generation_in_advance_days:
            if (
                generation_in_advance_days[RecurringTaskPeriod.WEEKLY] < 1
                or generation_in_advance_days[RecurringTaskPeriod.WEEKLY] > 7
            ):
                raise InputValidationError(
                    "Generation in advance days for weekly must be between 1 and 7"
                )
        if RecurringTaskPeriod.MONTHLY in generation_in_advance_days:
            if (
                generation_in_advance_days[RecurringTaskPeriod.MONTHLY] < 1
                or generation_in_advance_days[RecurringTaskPeriod.MONTHLY] > 30
            ):
                raise InputValidationError(
                    "Generation in advance days for monthly must be between 1 and 30"
                )
