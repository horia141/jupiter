"""A manager of Notion-side persons."""
import abc
from typing import Iterable

from domain.prm.person import Person
from models.basic import EntityId
from remote.notion.common import NotionPageLink


class PrmNotionManager(abc.ABC):
    """A manager of Notion-side persons."""

    @abc.abstractmethod
    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Upsert the root Notion structure."""

    @abc.abstractmethod
    def upsert_person(self, person: Person) -> None:
        """Upsert a person on Notion-side."""

    @abc.abstractmethod
    def remove_person(self, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""

    @abc.abstractmethod
    def load_all_saved_person_ref_ids(self) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""
