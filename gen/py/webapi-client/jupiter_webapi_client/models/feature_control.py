from enum import Enum


class FeatureControl(str, Enum):
    ALWAYS_OFF_HOSTING = "always-off-hosting"
    ALWAYS_OFF_TECH = "always-off-tech"
    ALWAYS_ON = "always-on"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
