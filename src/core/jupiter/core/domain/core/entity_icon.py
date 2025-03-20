"""The icon for an entity."""

from typing import cast

import emoji
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import RealmDecodingError
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@hashable_value
class EntityIcon(AtomicValue[str]):
    """The icon for an entity."""

    the_icon: str

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_icon


class EntityIconDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[EntityIcon]):
    """Encode to a database primitive."""

    def to_primitive(self, value: EntityIcon) -> Primitive:
        """Encode to a database primitive."""
        return value.the_icon


class EntityIconDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[EntityIcon]):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> EntityIcon:
        """Decode from a raw string."""
        entity_icon = value.strip()

        if entity_icon not in emoji.UNICODE_EMOJI_ENGLISH:
            entity_icon_try2 = cast(str, emoji.emojize(entity_icon)).strip()

            if entity_icon_try2 not in emoji.UNICODE_EMOJI_ENGLISH:
                raise RealmDecodingError("Expected an icon")

            return EntityIcon(entity_icon_try2)

        return EntityIcon(entity_icon)
