from enum import Enum


class EntityReferenceBlockKind(str, Enum):
    ENTITY_REFERENCE = "entity-reference"

    def __str__(self) -> str:
        return str(self.value)
