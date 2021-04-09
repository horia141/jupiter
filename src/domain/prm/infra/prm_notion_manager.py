"""A manager of Notion-side persons."""
import abc

from domain.prm.person import Person
from models.basic import EntityId


class PrmNotionManager(abc.ABC):
    """A manager of Notion-side persons."""

    @abc.abstractmethod
    def upsert_person(self, person: Person) -> None:
        """Upsert a person on Notion-side."""

    @abc.abstractmethod
    def remove_person(self, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""
