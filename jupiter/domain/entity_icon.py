"""The icon for an entity."""
from dataclasses import dataclass
from typing import Optional

import emoji

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value


@dataclass(frozen=True)
class EntityIcon(Value):
    """The icon for an entity."""

    _the_icon: str

    @staticmethod
    def from_raw(entity_icon_raw: Optional[str]) -> 'EntityIcon':
        """Validate and clean an entity icon."""
        if not entity_icon_raw:
            raise InputValidationError("Expected entity icon to be non-null")

        entity_icon = entity_icon_raw.strip()

        if entity_icon not in emoji.UNICODE_EMOJI_ENGLISH:
            entity_icon_try2 = emoji.emojize(entity_icon).strip()

            if entity_icon_try2 not in emoji.UNICODE_EMOJI_ENGLISH:
                raise InputValidationError("Expected an icon")

            return EntityIcon(entity_icon_try2)

        return EntityIcon(entity_icon)

    @staticmethod
    def from_safe(entity_icon_raw: str) -> 'EntityIcon':
        """Transform to an entity icon from a safe string."""
        return EntityIcon(entity_icon_raw)

    def to_safe(self) -> str:
        """Transform to an safe string."""
        return self._the_icon

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_icon
