"""A user avatar image."""

from typing import Optional

import avinit
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value


@hashable_value
class Avatar(AtomicValue):
    """A user avatar image."""

    avatar_as_data_url: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.avatar_as_data_url = self._clean_the_avatar(self.avatar_as_data_url)

    @staticmethod
    def from_user_name(user_name: UserName) -> "Avatar":
        """Construct an avatar from a user name."""
        avatar_as_data_url = avinit.get_avatar_data_url(user_name.the_name)
        return Avatar(avatar_as_data_url)

    @staticmethod
    def from_raw(avatar_raw: Optional[str]) -> "Avatar":
        """Construct an avatar from a string representation."""
        if avatar_raw is None:
            raise InputValidationError("Expected avatar to be non-null")

        return Avatar(Avatar._clean_the_avatar(avatar_raw))

    def to_primitive(self) -> Primitive:
        return self.avatar_as_data_url

    @staticmethod
    def _clean_the_avatar(avatar_raw: str) -> str:
        if not avatar_raw.startswith("data:image/svg+xml;base64,"):
            raise InputValidationError("Seems like the avatar doesn't look right")

        return avatar_raw
