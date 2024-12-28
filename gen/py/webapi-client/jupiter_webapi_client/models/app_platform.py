from enum import Enum


class AppPlatform(str, Enum):
    DESKTOP = "desktop"
    MOBILE_ANDROID = "mobile-android"
    MOBILE_IOS = "mobile-ios"
    TABLET_ANDROID = "tablet-android"
    TABLET_IOS = "tablet-ios"

    def __str__(self) -> str:
        return str(self.value)
