"""A certain activity that happens in a plan."""
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
from jupiter.core.domain.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsFieldRefId,
    LeafEntity,
    ParentLink,
    RefsAtMostOne,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class TimePlanActivity(LeafEntity):
    """A certain activity that happens in a plan."""

    time_plan: ParentLink

    target: TimePlanActivityTarget
    target_ref_id: EntityId
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability

    target_inbox_task = RefsAtMostOne(InboxTask, ref_id=IsFieldRefId("target_ref_id"))
    target_big_plan = RefsAtMostOne(BigPlan, ref_id=IsFieldRefId("target_ref_id"))

    @staticmethod
    @create_entity_action
    def new_activity_for_inbox_task(
        ctx: DomainContext,
        time_plan_ref_id: EntityId,
        inbox_task_ref_id: EntityId,
        kind: TimePlanActivityKind,
        feasability: TimePlanActivityFeasability,
    ) -> "TimePlanActivity":
        return TimePlanActivity._create(
            ctx,
            name=TimePlanActivity.build_name(
                TimePlanActivityTarget.INBOX_TASK, inbox_task_ref_id
            ),
            time_plan=ParentLink(time_plan_ref_id),
            target=TimePlanActivityTarget.INBOX_TASK,
            target_ref_id=inbox_task_ref_id,
            kind=kind,
            feasability=feasability,
        )

    @staticmethod
    @create_entity_action
    def new_activity_for_big_plan(
        ctx: DomainContext,
        time_plan_ref_id: EntityId,
        big_plan_ref_id: EntityId,
        kind: TimePlanActivityKind,
        feasability: TimePlanActivityFeasability,
    ) -> "TimePlanActivity":
        return TimePlanActivity._create(
            ctx,
            name=TimePlanActivity.build_name(
                TimePlanActivityTarget.INBOX_TASK, big_plan_ref_id
            ),
            time_plan=ParentLink(time_plan_ref_id),
            target=TimePlanActivityTarget.BIG_PLAN,
            target_ref_id=big_plan_ref_id,
            kind=kind,
            feasability=feasability,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        kind: UpdateAction[TimePlanActivityKind],
        feasability: UpdateAction[TimePlanActivityFeasability],
    ) -> "TimePlanActivity":
        return self._new_version(
            ctx,
            kind=kind.or_else(self.kind),
            feasability=feasability.or_else(self.feasability),
        )

    @staticmethod
    def build_name(target: TimePlanActivityTarget, entity_id: EntityId) -> EntityName:
        return EntityName(f"Work on {target} {entity_id}")
