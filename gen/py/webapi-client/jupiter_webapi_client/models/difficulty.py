from enum import Enum


class Difficulty(str, Enum):
    EASY = "easy"
    HARD = "hard"
    MEDIUM = "medium"

    def __str__(self) -> str:
        return str(self.value)
