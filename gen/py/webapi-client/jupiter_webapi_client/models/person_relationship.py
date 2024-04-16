from enum import Enum


class PersonRelationship(str, Enum):
    ACQUAINTANCE = "acquaintance"
    COLLEAGUE = "colleague"
    FAMILY = "family"
    FRIEND = "friend"
    OTHER = "other"
    SCHOOL_BUDDY = "school-buddy"
    WORK_BUDDY = "work-buddy"

    def __str__(self) -> str:
        return str(self.value)
