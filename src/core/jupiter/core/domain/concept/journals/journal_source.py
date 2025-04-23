"""The source of a journal entry."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class JournalSource(EnumValue):
    """The source of a journal entry."""

    USER = "user"
    GENERATED = "generated"

    @property
    def allow_user_changes(self) -> bool:
        """Whether the user can change the journal."""
        # Keep synced with ts:journal-source.ts
        return self == JournalSource.USER
