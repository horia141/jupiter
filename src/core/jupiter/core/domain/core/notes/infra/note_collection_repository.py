"""A repository of note collections."""
import abc

from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class NoteCollectionRepository(TrunkEntityRepository[NoteCollection], abc.ABC):
    """A repository of note collections."""
