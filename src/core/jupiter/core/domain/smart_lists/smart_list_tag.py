"""A smart list tag."""

from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafSupportEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class SmartListTag(LeafSupportEntity):
    """A smart list tag."""

    smart_list: ParentLink
    tag_name: TagName

    @staticmethod
    @create_entity_action
    def new_smart_list_tag(
        ctx: DomainContext,
        smart_list_ref_id: EntityId,
        tag_name: TagName,
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
        tag_name: UpdateAction[TagName],
    ) -> "SmartListTag":
        """Change the smart list tag."""
        return self._new_version(
            ctx,
            name=NOT_USED_NAME,
            tag_name=tag_name.or_else(self.tag_name),
        )
