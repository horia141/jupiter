from enum import Enum


class AppShell(str, Enum):
    BROWSER = "browser"
    CLI = "cli"
    DESKTOP_ELECTRON = "desktop-electron"
    MOBILE_CAPACITOR = "mobile-capacitor"
    PWA = "pwa"

    def __str__(self) -> str:
        return str(self.value)
