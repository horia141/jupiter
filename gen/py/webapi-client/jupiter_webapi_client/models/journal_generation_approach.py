from enum import Enum


class JournalGenerationApproach(str, Enum):
    BOTH_JOURNAL_AND_TASK = "both-journal-and-task"
    NONE = "none"
    ONLY_JOURNAL = "only-journal"

    def __str__(self) -> str:
        return str(self.value)
