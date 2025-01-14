"""The type of hosting jupiter is run into."""


from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class Hosting(EnumValue):
    """The type of hosting jupiter is run into."""

    HOSTED_GLOBAL = "hosted-global"
    LOCAL = "local"
