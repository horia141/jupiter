"""A manager of Notion-side persons."""
import abc
from typing import Iterable

from domain.prm.notion_person import NotionPerson
from domain.workspaces.notion_workspace import NotionWorkspace
from models.framework import EntityId, NotionId


class PrmNotionManager(abc.ABC):
    """A manager of Notion-side persons."""

    @abc.abstractmethod
    def upsert_root_notion_structure(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root Notion structure."""

    @abc.abstractmethod
    def upsert_person(self, notion_person: NotionPerson) -> None:
        """Upsert a person on Notion-side."""

    @abc.abstractmethod
    def save_person(self, notion_person: NotionPerson) -> None:
        """Save an already existing person on Notion-side."""

    @abc.abstractmethod
    def remove_person(self, ref_id: EntityId) -> None:
        """Remove a person on Notion-side."""

    @abc.abstractmethod
    def load_person_by_ref_id(self, ref_id: EntityId) -> NotionPerson:
        """Retrieve a person from Notion-side."""

    @abc.abstractmethod
    def load_all_persons(self) -> Iterable[NotionPerson]:
        """Retrieve all persons from Notion-side."""

    @abc.abstractmethod
    def load_all_saved_person_ref_ids(self) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def load_all_saved_person_notion_ids(self) -> Iterable[NotionId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def drop_all_persons(self) -> None:
        """Drop all persons on Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_entries(self, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""
