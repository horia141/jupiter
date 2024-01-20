"""A smart list tag."""
from typing import cast

from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    BranchTagEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class SmartListTag(BranchTagEntity):
    """A smart list tag."""

    smart_list: ParentLink

    @staticmethod
    @create_entity_action
    def new_smart_list_tag(
        ctx: DomainContext,
        smart_list_ref_id: EntityId,
        tag_name: SmartListTagName,
    ) -> "SmartListTag":
        """Create a smart list tag."""
        return SmartListTag._create(
            ctx,
            name=NOT_USED_NAME,
            smart_list=ParentLink(smart_list_ref_id),
            tag_name=tag_name,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        tag_name: UpdateAction[SmartListTagName],
    ) -> "SmartListTag":
        """Change the smart list tag."""
        return self._new_version(
            ctx,
            name=NOT_USED_NAME,
            tag_name=tag_name.or_else(cast(SmartListTagName, self.tag_name)),
        )
