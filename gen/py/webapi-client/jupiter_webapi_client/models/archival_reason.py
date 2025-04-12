from enum import Enum


class ArchivalReason(str, Enum):
    GC = "gc"
    SYNC = "sync"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
