"""The centralised point for interacting with the Notion PRM database."""
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.person import Person
from models.basic import EntityId


class NotionPrmManager(PrmNotionManager):
    """The centralised point for interacting with the Notion PRM database."""

    def upsert_person(self, person: Person) -> None:
        """Upsert a person on Notion-side."""

    def remove_person(self, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""
