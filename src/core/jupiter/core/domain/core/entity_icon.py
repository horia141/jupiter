"""The icon for an entity."""
from typing import Optional, cast

import emoji
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import AtomicValue, Value, hashable_value


@hashable_value
class EntityIcon(AtomicValue):
    """The icon for an entity."""

    the_icon: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_icon = self._clean_the_icon(self.the_icon)

    @staticmethod
    def from_raw(entity_icon_raw: Optional[str]) -> "EntityIcon":
        """Validate and clean an entity icon."""
        if not entity_icon_raw:
            raise InputValidationError("Expected entity icon to be non-null")

        return EntityIcon(EntityIcon._clean_the_icon(entity_icon_raw))

    @staticmethod
    def from_safe(entity_icon_raw: str) -> "EntityIcon":
        """Transform to an entity icon from a safe string."""
        return EntityIcon(entity_icon_raw)

    def to_safe(self) -> str:
        """Transform to an safe string."""
        return self.the_icon

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_icon

    @staticmethod
    def _clean_the_icon(entity_icon_raw: str) -> str:
        entity_icon = entity_icon_raw.strip()

        if entity_icon not in emoji.UNICODE_EMOJI_ENGLISH:
            entity_icon_try2 = cast(str, emoji.emojize(entity_icon)).strip()

            if entity_icon_try2 not in emoji.UNICODE_EMOJI_ENGLISH:
                raise InputValidationError("Expected an icon")

            return entity_icon_try2

        return entity_icon
