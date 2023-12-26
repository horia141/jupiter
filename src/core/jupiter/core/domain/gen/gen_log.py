"""A task generation log attched to a workspace."""
from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
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
class GenLog(TrunkEntity):
    """A log of task generation actions a user has performed."""

    workspace_ref_id: EntityId

    entries = ContainsMany(GenLogEntry, gen_log_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_gen_log(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "GenLog":
        """Create a new Gen log."""
        return GenLog._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )
