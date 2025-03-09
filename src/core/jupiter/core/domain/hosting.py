"""The type of hosting jupiter is run into."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class Hosting(EnumValue):
    """The type of hosting jupiter is run into."""

    HOSTED_GLOBAL = "hosted-global"
    SELF_HOSTED = "self-hosted"
    LOCAL = "local"

    def __str__(self) -> str:
        """The string representation of the hosting."""
        return self.value
