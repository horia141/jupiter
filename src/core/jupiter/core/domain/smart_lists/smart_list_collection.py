"""A smart list collection."""

from jupiter.core.domain.smart_lists.smart_list import SmartList
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
class SmartListCollection(TrunkEntity):
    """A smart list collection."""

    workspace_ref_id: EntityId

    smart_lists = ContainsMany(SmartList, smart_list_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_smart_list_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "SmartListCollection":
        """Create a smart list collection."""
        return SmartListCollection._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
