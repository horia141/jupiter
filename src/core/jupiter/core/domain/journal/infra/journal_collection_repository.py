"""The journal collection repository."""
import abc
from jupiter.core.domain.journal.journal_collection import JournalCollection
from jupiter.core.framework.repository import TrunkEntityRepository


class JournalCollectionRepository(
    TrunkEntityRepository[JournalCollection],
    abc.ABC,
):
    """A repository of journal collections."""