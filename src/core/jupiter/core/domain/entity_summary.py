"""The summary about an entity."""
from typing import Optional

from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import CrownEntity
from jupiter.core.framework.json import JSONDictType
from jupiter.core.framework.value import Value, value


@value
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
    def from_entity(entity: CrownEntity) -> "EntitySummary":
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

    @staticmethod
    def from_json(json: JSONDictType) -> "EntitySummary":
        """Create an entity summary from JSON."""
        # TODO: don't use str(x) here
        return EntitySummary(
            entity_tag=NamedEntityTag.from_raw(str(json["entity_tag"])),
            parent_ref_id=EntityId.from_raw(str(json["parent_ref_id"])),
            ref_id=EntityId.from_raw(str(json["ref_id"])),
            name=EntityName.from_raw(str(json["name"])),
            archived=bool(json["archived"]),
            created_time=Timestamp.from_raw(str(json["created_time"])),
            last_modified_time=Timestamp.from_raw(str(json["last_modified_time"])),
            archived_time=Timestamp.from_raw(str(json["archived_time"]))
            if json["archived_time"]
            else None,
            snippet=str(json["snippet"]),
        )

    def to_json(self) -> JSONDictType:
        """Convert the entity summary to JSON."""
        return {
            "entity_tag": self.entity_tag.value,
            "parent_ref_id": self.parent_ref_id.the_id,
            "ref_id": self.ref_id.the_id,
            "name": str(self.name),
            "archived": self.archived,
            "created_time": str(self.created_time),
            "last_modified_time": str(self.last_modified_time),
            "archived_time": str(self.archived_time) if self.archived_time else None,
            "snippet": str(self.name),
        }
