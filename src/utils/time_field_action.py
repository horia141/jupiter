"""What to do with a time denormalized field."""
import enum
from typing import Any


@enum.unique
class TimeFieldAction(enum.Enum):
    """What to do with a time denormalized field."""
    DO_NOTHING = "do-nothing"
    SET = "set"
    CLEAR = "clear"

    def act(self, obj: object, field: str, new_value: Any) -> None: # type: ignore
        """Act on an object's field and either set it or clear it."""
        if self == TimeFieldAction.SET:
            obj.__setattr__(field, new_value)
        elif self == TimeFieldAction.CLEAR:
            obj.__setattr__(field, None)
