"""The journal repository."""
import abc
from jupiter.core.domain.journal.journal import Journal
from jupiter.core.framework.repository import LeafEntityRepository


class JournalRepository(LeafEntityRepository[Journal], abc.ABC):
    """A repository of journals."""
