from enum import Enum


class Env(str, Enum):
    LOCAL = "local"
    PRODUCTION = "production"
    STAGING = "staging"

    def __str__(self) -> str:
        return str(self.value)
