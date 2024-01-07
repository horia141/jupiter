"""The journal repository."""
import abc

from jupiter.core.domain.journals.journal import Journal
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    LeafEntityRepository,
)


class JournalExistsForDatePeriodCombinationError(EntityAlreadyExistsError):
    """An error raised when a journal already exists for a date and period combination."""


class JournalRepository(LeafEntityRepository[Journal], abc.ABC):
    """A repository of journals."""
