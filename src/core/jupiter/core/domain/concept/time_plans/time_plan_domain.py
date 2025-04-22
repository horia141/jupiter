"""The time plan trunk domain object."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_generation_approach import (
    TimePlanGenerationApproach,
)
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    OwnsMany,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction


@entity
class TimePlanDomain(TrunkEntity):
    """A time plan trunk domain object."""

    workspace: ParentLink

    periods: set[RecurringTaskPeriod]
    generation_approach: TimePlanGenerationApproach
    generation_in_advance_days: dict[RecurringTaskPeriod, int]
    planning_task_project_ref_id: EntityId
    planning_task_gen_params: RecurringTaskGenParams | None

    time_plans = ContainsMany(TimePlan, time_plan_domain_ref_id=IsRefId())
    planning_task = OwnsMany(InboxTask, source=InboxTaskSource.TIME_PLAN)

    @staticmethod
    @create_entity_action
    def new_time_plan_domain(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        periods: set[RecurringTaskPeriod],
        generation_approach: TimePlanGenerationApproach,
        generation_in_advance_days: dict[RecurringTaskPeriod, int],
        planning_task_project_ref_id: EntityId,
        planning_task_eisen: Eisen | None,
        planning_task_difficulty: Difficulty | None,
    ) -> "TimePlanDomain":
        """Create a new time plan domain."""
        final_generation_in_advance_days: dict[RecurringTaskPeriod, int]
        if generation_approach == TimePlanGenerationApproach.NONE:
            if len(generation_in_advance_days) > 0:
                raise InputValidationError(
                    "Generation in advance days cannot be set if generation approach is NONE"
                )
            if planning_task_eisen is not None:
                raise InputValidationError(
                    "Planning task eisen cannot be set if generation approach is NONE"
                )
            if planning_task_difficulty is not None:
                raise InputValidationError(
                    "Planning task difficulty cannot be set if generation approach is NONE"
                )
            final_generation_in_advance_days = {}
            final_planning_task_gen_params = None
        elif generation_approach == TimePlanGenerationApproach.ONLY_PLAN:
            if periods != generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is ONLY_PLAN"
                )
            if planning_task_eisen is not None:
                raise InputValidationError(
                    "Planning task eisen cannot be set if generation approach is NONE"
                )
            if planning_task_difficulty is not None:
                raise InputValidationError(
                    "Planning task difficulty cannot be set if generation approach is NONE"
                )
            final_generation_in_advance_days = {}
            final_planning_task_gen_params = None
        elif generation_approach == TimePlanGenerationApproach.BOTH_PLAN_AND_TASK:
            if periods != generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is BOTH_PLAN_AND_TASK"
                )
            if planning_task_eisen is None:
                raise InputValidationError(
                    "Planning task eisen must be set if generation approach is ONLY_TASK"
                )
            if planning_task_difficulty is None:
                raise InputValidationError(
                    "Planning task difficulty must be set if generation approach is BOTH_PLAN_AND_TASK"
                )
            final_generation_in_advance_days = generation_in_advance_days
            final_planning_task_gen_params = RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=planning_task_eisen,
                difficulty=planning_task_difficulty,
                actionable_from_day=None,
                actionable_from_month=None,
                due_at_day=None,
                due_at_month=None,
                skip_rule=None,
            )
        TimePlanDomain._validate_generation_in_advance_days(
            final_generation_in_advance_days
        )
        return TimePlanDomain._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=final_generation_in_advance_days,
            planning_task_project_ref_id=planning_task_project_ref_id,
            planning_task_gen_params=final_planning_task_gen_params,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        periods: UpdateAction[set[RecurringTaskPeriod]],
        generation_approach: UpdateAction[TimePlanGenerationApproach],
        generation_in_advance_days: UpdateAction[dict[RecurringTaskPeriod, int]],
        planning_task_project_ref_id: UpdateAction[EntityId],
        planning_task_eisen: UpdateAction[Eisen | None],
        planning_task_difficulty: UpdateAction[Difficulty | None],
    ) -> "TimePlanDomain":
        """Update the time plan domain."""
        final_periods = periods.or_else(self.periods)
        final_generation_approach = generation_approach.or_else(
            self.generation_approach
        )
        final_generation_in_advance_days = generation_in_advance_days.or_else(
            self.generation_in_advance_days
        )
        final_planning_task_project_ref_id = planning_task_project_ref_id.or_else(
            self.planning_task_project_ref_id
        )
        final_planning_task_eisen = planning_task_eisen.or_else(
            self.planning_task_gen_params.eisen
            if self.planning_task_gen_params is not None
            else None
        )
        final_planning_task_difficulty = planning_task_difficulty.or_else(
            self.planning_task_gen_params.difficulty
            if self.planning_task_gen_params is not None
            else None
        )

        if final_generation_approach == TimePlanGenerationApproach.NONE:
            if len(final_generation_in_advance_days) > 0:
                raise InputValidationError(
                    "Generation in advance days cannot be set if generation approach is NONE"
                )
            if final_planning_task_eisen is not None:
                raise InputValidationError(
                    "Planning task eisen cannot be set if generation approach is NONE"
                )
            if final_planning_task_difficulty is not None:
                raise InputValidationError(
                    "Planning task difficulty cannot be set if generation approach is NONE"
                )
            final_planning_task_gen_params = None
        elif final_generation_approach == TimePlanGenerationApproach.ONLY_PLAN:
            if final_periods != final_generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is ONLY_PLAN"
                )
            if final_planning_task_eisen is not None:
                raise InputValidationError(
                    "Planning task eisen cannot be set if generation approach is NONE"
                )
            if final_planning_task_difficulty is not None:
                raise InputValidationError(
                    "Planning task difficulty cannot be set if generation approach is NONE"
                )
            final_planning_task_gen_params = None
        elif final_generation_approach == TimePlanGenerationApproach.BOTH_PLAN_AND_TASK:
            if final_periods != final_generation_in_advance_days.keys():
                raise InputValidationError(
                    "Periods must be set if generation approach is BOTH_PLAN_AND_TASK"
                )
            if final_planning_task_eisen is None:
                raise InputValidationError(
                    "Planning task eisen must be set if generation approach is ONLY_TASK"
                )
            if final_planning_task_difficulty is None:
                raise InputValidationError(
                    "Planning task difficulty must be set if generation approach is BOTH_PLAN_AND_TASK"
                )
            final_planning_task_gen_params = RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=final_planning_task_eisen,
                difficulty=final_planning_task_difficulty,
                actionable_from_day=None,
                actionable_from_month=None,
                due_at_day=None,
                due_at_month=None,
                skip_rule=None,
            )
        TimePlanDomain._validate_generation_in_advance_days(
            final_generation_in_advance_days
        )

        return self._new_version(
            ctx,
            periods=final_periods,
            generation_approach=final_generation_approach,
            generation_in_advance_days=final_generation_in_advance_days,
            planning_task_project_ref_id=final_planning_task_project_ref_id,
            planning_task_gen_params=final_planning_task_gen_params,
        )

    @update_entity_action
    def change_planning_task_project_if_required(
        self,
        ctx: DomainContext,
        planning_task_project_ref_id: EntityId,
    ) -> "TimePlanDomain":
        """Change the planning task project."""
        return self._new_version(
            ctx,
            planning_task_project_ref_id=planning_task_project_ref_id,
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
        if RecurringTaskPeriod.QUARTERLY in generation_in_advance_days:
            if (
                generation_in_advance_days[RecurringTaskPeriod.QUARTERLY] < 1
                or generation_in_advance_days[RecurringTaskPeriod.QUARTERLY] > 90
            ):
                raise InputValidationError(
                    "Generation in advance days for quarterly must be between 1 and 90"
                )
        if RecurringTaskPeriod.YEARLY in generation_in_advance_days:
            if (
                generation_in_advance_days[RecurringTaskPeriod.YEARLY] < 1
                or generation_in_advance_days[RecurringTaskPeriod.YEARLY] > 365
            ):
                raise InputValidationError(
                    "Generation in advance days for yearly must be between 1 and 365"
                )
