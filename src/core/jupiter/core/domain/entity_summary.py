"""The summary about an entity."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import BranchEntity, LeafEntity
from jupiter.core.framework.value import Value


@dataclass
class EntitySummary(Value):
    """Information about a particular entity very broadly."""

    entity_tag: NamedEntityTag
    parent_ref_id: EntityId
    ref_id: EntityId
    name: EntityName
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]
    snippet: str

    @staticmethod
    def from_entity(entity: BranchEntity | LeafEntity) -> "EntitySummary":
        """Create an entity summary from an entity."""
        return EntitySummary(
            entity_tag=NamedEntityTag.from_entity(entity),
            parent_ref_id=entity.parent_ref_id,
            ref_id=entity.ref_id,
            name=entity.name,
            archived=entity.archived,
            created_time=entity.created_time,
            last_modified_time=entity.last_modified_time,
            archived_time=entity.archived_time,
            snippet=str(entity.name),
        )
