"""A certain activity that happens in a plan."""
import abc

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
    RefsAtMostOneCond,
    SelfCond,
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
class TimePlanActivity(LeafEntity):
    """A certain activity that happens in a plan."""

    time_plan: ParentLink

    target: TimePlanActivityTarget
    target_ref_id: EntityId
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability

    target_inbox_task = RefsAtMostOneCond(
        InboxTask,
        SelfCond(target=TimePlanActivityTarget.INBOX_TASK),
        ref_id=IsFieldRefId("target_ref_id"),
    )
    target_big_plan = RefsAtMostOneCond(
        BigPlan,
        SelfCond(target=TimePlanActivityTarget.BIG_PLAN),
        ref_id=IsFieldRefId("target_ref_id"),
    )

    @staticmethod
    @create_entity_action
    def new_activity_from_existing(
        ctx: DomainContext,
        time_plan_ref_id: EntityId,
        existing_activity_name: EntityName,
        existing_activity_target: TimePlanActivityTarget,
        existing_activity_target_ref_id: EntityId,
        existing_activity_kind: TimePlanActivityKind,
        existing_activity_feasability: TimePlanActivityFeasability,
    ) -> "TimePlanActivity":
        """Create a new actvity from an existing one."""
        return TimePlanActivity._create(
            ctx,
            name=existing_activity_name,
            time_plan=ParentLink(time_plan_ref_id),
            target=existing_activity_target,
            target_ref_id=existing_activity_target_ref_id,
            kind=existing_activity_kind,
            feasability=existing_activity_feasability,
        )

    @staticmethod
    @create_entity_action
    def new_activity_for_inbox_task(
        ctx: DomainContext,
        time_plan_ref_id: EntityId,
        inbox_task_ref_id: EntityId,
        kind: TimePlanActivityKind,
        feasability: TimePlanActivityFeasability,
    ) -> "TimePlanActivity":
        """Create a new activity from an inbox task."""
        return TimePlanActivity._create(
            ctx,
            name=TimePlanActivity._build_name(
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
        """Create a new activity from a big plan."""
        return TimePlanActivity._create(
            ctx,
            name=TimePlanActivity._build_name(
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
        """Update the details of an activity."""
        return self._new_version(
            ctx,
            kind=kind.or_else(self.kind),
            feasability=feasability.or_else(self.feasability),
        )

    @staticmethod
    def _build_name(target: TimePlanActivityTarget, entity_id: EntityId) -> EntityName:
        return EntityName(f"Work on {target.value!s} {entity_id}")


class TimePlanAlreadyAssociatedWithTargetError(EntityAlreadyExistsError):
    """An error raised when a time plan is already associated with a target entity."""


class TimePlanActivityRespository(LeafEntityRepository[TimePlanActivity], abc.ABC):
    """An error raised when a time plan is already associated with a target entity."""

    @abc.abstractmethod
    async def find_all_with_target(
        self,
        target: TimePlanActivityTarget,
        target_ref_id: EntityId,
    ) -> list[EntityId]:
        """Find all time plan ids with a certain entity in their activity set."""
