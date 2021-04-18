"""The centralised point for interacting with the Notion PRM database."""
from typing import Iterable

from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.notion_person import NotionPerson
from domain.prm.person import Person
from models.basic import EntityId
from remote.notion.common import NotionPageLink, NotionId


class NotionPrmManager(PrmNotionManager):
    """The centralised point for interacting with the Notion PRM database."""

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Upsert the root Notion structure."""

    def upsert_person(self, person: Person) -> None:
        """Upsert a person on Notion-side."""

    def save_person(self, notion_person: NotionPerson) -> None:
        """Save an already existing person on Notion-side."""

    def remove_person(self, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""

    def load_all_persons(self) -> Iterable[NotionPerson]:
        """Retrieve all persons from Notion-side."""

    def load_all_saved_person_ref_ids(self) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    def load_all_saved_person_notion_ids(self) -> Iterable[NotionId]:
        """Load ids of all persons we know about from Notion side."""

    def drop_all_persons(self) -> None:
        """Drop all persons on Notion-side."""

    def link_local_and_notion_entries(self, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""
