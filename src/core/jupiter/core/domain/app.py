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


@enum_value
class AppPlatform(EnumValue):
    """The platform on which the app is running."""

    DESKTOP = "desktop"
    MOBILE_IOS = "mobile-ios"
    MOBILE_ANDROID = "mobile-android"
    TABLET_IOS = "tablet-ios"
    TABLET_ANDROID = "tablet-android"
