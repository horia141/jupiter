"""A user avatar image."""
import avinit
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@hashable_value
class Avatar(AtomicValue[str]):
    """A user avatar image."""

    avatar_as_data_url: str

    @staticmethod
    def from_user_name(user_name: UserName) -> "Avatar":
        """Construct an avatar from a user name."""
        avatar_as_data_url = avinit.get_avatar_data_url(user_name.the_name)
        return Avatar(avatar_as_data_url)


class AvatarDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[Avatar]):
    """Encode to a database primitive."""

    def to_primitive(self, value: Avatar) -> Primitive:
        """Encode to a database primitive."""
        return value.avatar_as_data_url


class AvatarDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[Avatar]):
    """Decode from a database primitive."""

    def from_raw_str(self, primitive: str) -> Avatar:
        """Decode from a raw string."""
        if not primitive.startswith("data:image/svg+xml;base64,"):
            raise InputValidationError("Seems like the avatar doesn't look right")

        return Avatar(primitive)
