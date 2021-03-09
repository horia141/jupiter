"""A manager of Notion-side vacations."""
import abc

from domain.vacations.vacation import Vacation
from models.basic import EntityId


class VacationNotionManager(abc.ABC):
    """A manager of Notion-side vacations."""

    @abc.abstractmethod
    def upsert_vacation(self, vacation: Vacation) -> None:
        """Upsert a vacation on Notion-side."""

    @abc.abstractmethod
    def remove_vacation(self, ref_id: EntityId) -> None:
        """Remove a vacation on Notion-side."""
