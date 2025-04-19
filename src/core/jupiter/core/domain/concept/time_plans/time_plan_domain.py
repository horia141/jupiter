"""The time plan trunk domain object."""

from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_generation_approach import TimePlanGenerationApproach
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
class TimePlanDomain(TrunkEntity):
    """A time plan trunk domain object."""

    workspace: ParentLink

    periods: set[RecurringTaskPeriod]
    generation_approach: TimePlanGenerationApproach
    planning_task_project_ref_id: EntityId | None
    planning_task_gen_params: RecurringTaskGenParams | None

    time_plans = ContainsMany(TimePlan, time_plan_domain_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_time_plan_domain(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        periods: set[RecurringTaskPeriod],
        generation_approach: TimePlanGenerationApproach,
        planning_task_project_ref_id: EntityId | None,
        planning_task_eisen: Eisen | None,
        planning_task_difficulty: Difficulty | None,
    ) -> "TimePlanDomain":
        """Create a new time plan domain."""
        if generation_approach == TimePlanGenerationApproach.NONE or generation_approach == TimePlanGenerationApproach.ONLY_PLAN:
            if planning_task_project_ref_id is not None:
                raise InputValidationError("Planning task project ref id cannot be set if generation approach is NONE")
            if planning_task_eisen is not None:
                raise InputValidationError("Planning task eisen cannot be set if generation approach is NONE")
            if planning_task_difficulty is not None:
                raise InputValidationError("Planning task difficulty cannot be set if generation approach is NONE")
            final_planning_task_project_ref_id = None
            final_planning_task_gen_params = None
        if generation_approach == TimePlanGenerationApproach.BOTH_PLAN_AND_TASK:
            if planning_task_project_ref_id is None:
                raise InputValidationError("Planning task project ref id must be set if generation approach is BOTH_PLAN_AND_TASK")
            if planning_task_eisen is None:
                raise InputValidationError("Planning task eisen must be set if generation approach is ONLY_TASK")
            if planning_task_difficulty is None:
                raise InputValidationError("Planning task difficulty must be set if generation approach is BOTH_PLAN_AND_TASK")
            final_planning_task_project_ref_id = planning_task_project_ref_id
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
        return TimePlanDomain._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            periods=periods,
            generation_approach=generation_approach,
            planning_task_project_ref_id=final_planning_task_project_ref_id,
            planning_task_gen_params=final_planning_task_gen_params,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        periods: UpdateAction[set[RecurringTaskPeriod]],
        generation_approach: UpdateAction[TimePlanGenerationApproach],
        planning_task_project_ref_id: UpdateAction[EntityId | None],
        planning_task_eisen: UpdateAction[Eisen | None],
        planning_task_difficulty: UpdateAction[Difficulty | None],
    ) -> "TimePlanDomain":
        """Update the time plan domain."""
        if generation_approach.should_change:
            final_planning_task_project_ref_id: EntityId | None = None
            final_planning_task_eisen: Eisen | None = None
            final_planning_task_difficulty: Difficulty | None = None
            final_planning_task_gen_params: RecurringTaskGenParams | None = None
            if generation_approach.just_the_value == TimePlanGenerationApproach.NONE or generation_approach.just_the_value == TimePlanGenerationApproach.ONLY_PLAN:
                if planning_task_project_ref_id.test(lambda x: x is not None):
                    raise InputValidationError("Planning task project ref id cannot be set if generation approach is NONE")
                if planning_task_eisen.test(lambda x: x is not None):
                    raise InputValidationError("Planning task eisen cannot be set if generation approach is NONE")
                if planning_task_difficulty.test(lambda x: x is not None):
                    raise InputValidationError("Planning task difficulty cannot be set if generation approach is NONE")
                final_planning_task_project_ref_id = None
                final_planning_task_gen_params = None
            if generation_approach.just_the_value == TimePlanGenerationApproach.BOTH_PLAN_AND_TASK:
                final_planning_task_project_ref_id = planning_task_project_ref_id.or_else(self.planning_task_project_ref_id)
                if final_planning_task_project_ref_id is None:
                    raise InputValidationError("Planning task project ref id must be set if generation approach is BOTH_PLAN_AND_TASK")
                final_planning_task_eisen = planning_task_eisen.or_else(self.planning_task_gen_params.eisen if self.planning_task_gen_params is not None else None)
                if final_planning_task_eisen is None:
                    raise InputValidationError("Planning task eisen must be set if generation approach is BOTH_PLAN_AND_TASK")
                final_planning_task_difficulty = planning_task_difficulty.or_else(self.planning_task_gen_params.difficulty if self.planning_task_gen_params is not None else None)
                if final_planning_task_difficulty is None:
                    raise InputValidationError("Planning task difficulty must be set if generation approach is BOTH_PLAN_AND_TASK")
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
        return self._new_version(
            ctx,
            periods=periods.or_else(self.periods),
            generation_approach=generation_approach.or_else(self.generation_approach),
            planning_task_project_ref_id=final_planning_task_project_ref_id,
            planning_task_gen_params=final_planning_task_gen_params,
        )

    @update_entity_action
    def change_planning_task_project(
        self,
        ctx: DomainContext,
        planning_task_project_ref_id: EntityId,
    ) -> "TimePlanDomain":
        """Change the planning task project."""
        return self._new_version(
            ctx,
            planning_task_project_ref_id=planning_task_project_ref_id,
        )

    def get_gen_params_for_period(self, period: RecurringTaskPeriod) -> RecurringTaskGenParams: