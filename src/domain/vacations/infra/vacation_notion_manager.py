"""A manager of Notion-side vacations."""
import abc
from typing import Iterable

from domain.vacations.notion_vacation import NotionVacation
from domain.vacations.vacation import Vacation
from domain.workspaces.notion_workspace import NotionWorkspace
from models.framework import EntityId, NotionId


class VacationNotionManager(abc.ABC):
    """A manager of Notion-side vacations."""

    @abc.abstractmethod
    def upsert_root_page(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root page structure for vacations."""

    @abc.abstractmethod
    def upsert_vacation(self, vacation: Vacation) -> NotionVacation:
        """Upsert a vacation on Notion-side."""

    @abc.abstractmethod
    def save_vacation(self, vacation: NotionVacation) -> NotionVacation:
        """Upsert a vacation on Notion-side."""

    @abc.abstractmethod
    def remove_vacation(self, ref_id: EntityId) -> None:
        """Remove a vacation on Notion-side."""

    @abc.abstractmethod
    def load_all_vacations(self) -> Iterable[NotionVacation]:
        """Load all Notion-side vacations."""

    @abc.abstractmethod
    def load_all_saved_vacation_ref_ids(self) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def load_all_saved_vacation_notion_ids(self) -> Iterable[NotionId]:
        """Load ids of all vacations we know about from Notion side."""

    @abc.abstractmethod
    def drop_all_vacations(self) -> None:
        """Remove all vacations on Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_entries(self, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""
