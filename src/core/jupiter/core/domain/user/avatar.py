"""A user avatar image."""


import avinit
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value


@hashable_value
class Avatar(AtomicValue):
    """A user avatar image."""

    avatar_as_data_url: str

    @staticmethod
    def from_user_name(user_name: UserName) -> "Avatar":
        """Construct an avatar from a user name."""
        avatar_as_data_url = avinit.get_avatar_data_url(user_name.the_name)
        return Avatar(avatar_as_data_url)

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "Avatar":
        """Construct an avatar from a string representation."""
        if not isinstance(value, str):
            raise InputValidationError("Expected avatar to be a string")

        return Avatar(Avatar._clean_the_avatar(value))

    def to_primitive(self) -> Primitive:
        return self.avatar_as_data_url

    @staticmethod
    def _clean_the_avatar(avatar_raw: str) -> str:
        if not avatar_raw.startswith("data:image/svg+xml;base64,"):
            raise InputValidationError("Seems like the avatar doesn't look right")

        return avatar_raw
