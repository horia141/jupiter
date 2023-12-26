"""A habit collection."""

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class HabitCollection(TrunkEntity):
    """A habit collection."""

    workspace_ref_id: EntityId

    habits = ContainsMany(Habit, habit_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_habit_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "HabitCollection":
        """Create a habit collection."""
        return HabitCollection._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
