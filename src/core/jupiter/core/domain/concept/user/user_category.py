"""The category of user."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class UserCategory(EnumValue):
    """The category of user."""

    STANDARD = "standard"
    APP_STORE_REVIEW = "app-store-test"
