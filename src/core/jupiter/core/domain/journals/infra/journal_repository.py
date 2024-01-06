"""The journal repository."""
import abc

from jupiter.core.domain.journals.journal import Journal
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    LeafEntityRepository,
)


class JournalExistsForPeriodAndDateError(EntityAlreadyExistsError):
    """An error raised when a journal already exists for a period and date."""


class JournalRepository(LeafEntityRepository[Journal], abc.ABC):
    """A repository of journals."""
