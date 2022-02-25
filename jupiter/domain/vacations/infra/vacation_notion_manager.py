"""A manager of Notion-side vacations."""
import abc
from typing import Iterable

from jupiter.domain.vacations.notion_vacation import NotionVacation
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId


class NotionVacationNotFoundError(Exception):
    """Exception raised when a Notion vacation was not found."""


class VacationNotionManager(abc.ABC):
    """A manager of Notion-side vacations."""

    @abc.abstractmethod
    def upsert_root_page(
            self, notion_workspace: NotionWorkspace, vacation_collection: NotionVacationCollection) -> None:
        """Upsert the root page structure for vacations."""

    @abc.abstractmethod
    def upsert_vacation(self, vacation_collection_ref_id: EntityId, vacation: NotionVacation) -> NotionVacation:
        """Upsert a vacation on Notion-side."""

    @abc.abstractmethod
    def save_vacation(self, vacation_collection_ref_id: EntityId, vacation: NotionVacation) -> NotionVacation:
        """Upsert a vacation on Notion-side."""

    @abc.abstractmethod
    def load_vacation(self, vacation_collection_ref_id: EntityId, ref_id: EntityId) -> NotionVacation:
        """Load a Notion-side vacation."""

    @abc.abstractmethod
    def load_all_vacations(self, vacation_collection_ref_id: EntityId) -> Iterable[NotionVacation]:
        """Load all Notion-side vacations."""

    @abc.abstractmethod
    def remove_vacation(self, vacation_collection_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a vacation on Notion-side."""

    @abc.abstractmethod
    def drop_all_vacations(self, vacation_collection_ref_id: EntityId) -> None:
        """Remove all vacations on Notion-side."""

    @abc.abstractmethod
    def load_all_saved_vacation_ref_ids(self, vacation_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def load_all_saved_vacation_notion_ids(self, vacation_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Load ids of all vacations we know about from Notion side."""

    @abc.abstractmethod
    def link_local_and_notion_entries(
            self, vacation_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""
