from enum import Enum


class AppCore(str, Enum):
    CLI = "cli"
    WEBUI = "webui"

    def __str__(self) -> str:
        return str(self.value)
