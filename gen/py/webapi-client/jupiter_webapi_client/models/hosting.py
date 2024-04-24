from enum import Enum


class Hosting(str, Enum):
    HOSTED_GLOBAL = "hosted-global"
    LOCAL = "local"

    def __str__(self) -> str:
        return str(self.value)