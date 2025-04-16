"""The time plan trunk domain object."""

from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
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
    planning_task_project_ref_id: EntityId
    planning_task_gen_params: RecurringTaskGenParams
    days_until_gc: int

    time_plans = ContainsMany(TimePlan, time_plan_domain_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_time_plan_domain(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        periods: set[RecurringTaskPeriod],
        planning_task_project_ref_id: EntityId,
        planning_task_eisen: Eisen,
        planning_task_difficulty: Difficulty,
        days_until_gc: int,
    ) -> "TimePlanDomain":
        """Create a new time plan domain."""
        if days_until_gc < 0:
            raise InputValidationError("Days until gc cannot be negative")
        if days_until_gc > 30:
            raise InputValidationError("Days until GC cannot be larger than 30")
        return TimePlanDomain._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            periods=periods,
            planning_task_project_ref_id=planning_task_project_ref_id,
            planning_task_gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=planning_task_eisen,
                difficulty=planning_task_difficulty,
                actionable_from_day=None,
                actionable_from_month=None,
                due_at_day=None,
                due_at_month=None,
                skip_rule=None,
            ),
            days_until_gc=days_until_gc,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        periods: UpdateAction[set[RecurringTaskPeriod]],
        planning_task_project_ref_id: UpdateAction[EntityId],
        planning_task_eisen: UpdateAction[Eisen],
        planning_task_difficulty: UpdateAction[Difficulty],
        days_until_gc: UpdateAction[int],
    ) -> "TimePlanDomain":
        """Update the time plan domain."""
        if days_until_gc.test(lambda x: x < 0):
            raise InputValidationError("Days until gc cannot be negative")
        if days_until_gc.test(lambda x: x > 30):
            raise InputValidationError("Days until GC cannot be larger than 30")
        return self._new_version(
            ctx,
            periods=periods.or_else(self.periods),
            planning_task_project_ref_id=planning_task_project_ref_id.or_else(
                self.planning_task_project_ref_id
            ),
            planning_task_gen_params=(
                RecurringTaskGenParams(
                    period=self.planning_task_gen_params.period,
                    eisen=planning_task_eisen.or_else(
                        self.planning_task_gen_params.eisen
                    ),
                    difficulty=planning_task_difficulty.or_else(
                        self.planning_task_gen_params.difficulty
                    ),
                    actionable_from_day=None,
                    actionable_from_month=None,
                    due_at_day=None,
                    due_at_month=None,
                    skip_rule=None,
                )
                if planning_task_eisen.should_change
                or planning_task_difficulty.should_change
                else self.planning_task_gen_params
            ),
            days_until_gc=days_until_gc.or_else(self.days_until_gc),
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
