"""The approach to generate journals."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class JournalGenerationApproach(EnumValue):
    """The approach to generate journals."""

    BOTH_JOURNAL_AND_TASK = "both-journal-and-task"
    ONLY_JOURNAL = "only-journal"
    NONE = "none"

    @property
    def should_do_nothing(self) -> bool:
        """Whether to do nothing."""
        return self == JournalGenerationApproach.NONE

    @property
    def should_generate_a_journal(self) -> bool:
        """Whether to generate a journal."""
        return (
            self == JournalGenerationApproach.BOTH_JOURNAL_AND_TASK
            or self == JournalGenerationApproach.ONLY_JOURNAL
        )

    @property
    def should_generate_a_writing_task(self) -> bool:
        """Whether to generate a writing task."""
        return self == JournalGenerationApproach.BOTH_JOURNAL_AND_TASK

    @property
    def should_not_generate_a_journal(self) -> bool:
        """Whether to not generate a journal."""
        return self == JournalGenerationApproach.NONE

    @property
    def should_not_generate_a_writing_task(self) -> bool:
        """Whether to not generate a writing task."""
        return (
            self == JournalGenerationApproach.NONE
            or self == JournalGenerationApproach.ONLY_JOURNAL
        )
