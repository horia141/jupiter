"""A client facing application."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class AppCore(EnumValue):
    """A client facing application."""

    CLI = "cli"
    WEBUI = "webui"


@enum_value
class AppShell(EnumValue):
    """A shell that wraps a given app."""

    CLI = "cli"
    BROWSER = "browser"
    DESKTOP_ELECTRON = "desktop-electron"
    MOBILE_CAPACITOR = "mobile-capacitor"
    MOBILE_PWA = "mobile-pwa"
