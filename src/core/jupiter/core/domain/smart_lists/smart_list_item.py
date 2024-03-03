"""A smart list item."""
from typing import List, Optional

from jupiter.core.domain.core.url import URL
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsOneOfRefId,
    IsParentLink,
    LeafEntity,
    ParentLink,
    RefsMany,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class SmartListItem(LeafEntity):
    """A smart list item."""

    smart_list: ParentLink
    name: SmartListItemName
    is_done: bool
    tags_ref_id: list[EntityId]
    url: Optional[URL]

    tags = RefsMany(SmartListTag, ref_id=IsOneOfRefId("tags_ref_id"))
    all_tags = RefsMany(SmartListTag, smart_list_ref_id=IsParentLink())

    @staticmethod
    @create_entity_action
    def new_smart_list_item(
        ctx: DomainContext,
        smart_list_ref_id: EntityId,
        name: SmartListItemName,
        is_done: bool,
        tags_ref_id: List[EntityId],
        url: Optional[URL],
    ) -> "SmartListItem":
        """Create a smart list item."""
        return SmartListItem._create(
            ctx,
            smart_list=ParentLink(smart_list_ref_id),
            name=name,
            is_done=is_done,
            tags_ref_id=tags_ref_id,
            url=url,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[SmartListItemName],
        is_done: UpdateAction[bool],
        tags_ref_id: UpdateAction[List[EntityId]],
        url: UpdateAction[Optional[URL]],
    ) -> "SmartListItem":
        """Update the smart list item."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            is_done=is_done.or_else(self.is_done),
            tags_ref_id=tags_ref_id.or_else(self.tags_ref_id),
            url=url.or_else(self.url),
        )
