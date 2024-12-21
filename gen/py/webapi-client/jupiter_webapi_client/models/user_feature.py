from enum import Enum


class UserFeature(str, Enum):
    GAMIFICATION = "gamification"

    def __str__(self) -> str:
        return str(self.value)
