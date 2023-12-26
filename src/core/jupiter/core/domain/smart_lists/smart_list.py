"""A smart list."""
from typing import Optional

from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    BranchEntity,
    ContainsMany,
    IsRefId,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class SmartList(BranchEntity):
    """A smart list."""

    smart_list_collection_ref_id: EntityId
    name: SmartListName
    icon: Optional[EntityIcon]

    items = ContainsMany(SmartListItem, smart_list_ref_id=IsRefId())
    tags = ContainsMany(SmartListTag, smart_list_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_smart_list(
        ctx: DomainContext,
        smart_list_collection_ref_id: EntityId,
        name: SmartListName,
        icon: Optional[EntityIcon],
    ) -> "SmartList":
        """Create a smart list."""
        return SmartList._create(
            ctx,
            smart_list_collection_ref_id=smart_list_collection_ref_id,
            name=name,
            icon=icon,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[SmartListName],
        icon: UpdateAction[Optional[EntityIcon]],
    ) -> "SmartList":
        """Change the name of the smart list."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            icon=icon.or_else(self.icon),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.smart_list_collection_ref_id
