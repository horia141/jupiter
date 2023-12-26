"""A vacation collection."""
from jupiter.core.domain.vacations.vacation import Vacation
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
class VacationCollection(TrunkEntity):
    """A vacation collection."""

    workspace_ref_id: EntityId

    vacations = ContainsMany(Vacation, vacation_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_vacation_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "VacationCollection":
        """Create a vacation collection."""
        return VacationCollection._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
