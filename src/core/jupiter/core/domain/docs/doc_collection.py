"""The doc collection."""
from jupiter.core.domain.docs.doc import Doc
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
class DocCollection(TrunkEntity):
    """A doc collection."""

    workspace_ref_id: EntityId

    docs = ContainsMany(Doc, doc_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_doc_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "DocCollection":
        """Create a inbox task collection."""
        return DocCollection._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
