"""A manager of Notion-side persons."""
import abc
from typing import Iterable

from jupiter.domain.persons.notion_person import NotionPerson
from jupiter.domain.persons.notion_person_collection import NotionPersonCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId


class NotionPersonNotFoundError(Exception):
    """Exception raised when a Notion person was not found."""


class PersonNotionManager(abc.ABC):
    """A manager of Notion-side persons."""

    @abc.abstractmethod
    def upsert_root_page(self, notion_workspace: NotionWorkspace, person_collection: NotionPersonCollection) -> None:
        """Upsert the root Notion structure."""

    @abc.abstractmethod
    def upsert_person(self, person_collection_ref_id: EntityId, notion_person: NotionPerson) -> None:
        """Upsert a person on Notion-side."""

    @abc.abstractmethod
    def save_person(self, person_collection_ref_id: EntityId, notion_person: NotionPerson) -> None:
        """Save an already existing person on Notion-side."""

    @abc.abstractmethod
    def load_person(self, person_collection_ref_id: EntityId, ref_id: EntityId) -> NotionPerson:
        """Retrieve a person from Notion-side."""

    @abc.abstractmethod
    def load_all_persons(self, person_collection_ref_id: EntityId) -> Iterable[NotionPerson]:
        """Retrieve all persons from Notion-side."""

    @abc.abstractmethod
    def remove_person(self, person_collection_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""

    @abc.abstractmethod
    def drop_all_persons(self, person_collection_ref_id: EntityId) -> None:
        """Drop all persons on Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_entries(
            self, person_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""

    @abc.abstractmethod
    def load_all_saved_person_ref_ids(self, person_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def load_all_saved_person_notion_ids(self, person_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Load ids of all persons we know about from Notion side."""
