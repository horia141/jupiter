"""A repository of vacations."""
import abc

from jupiter.domain.vacations.vacation import Vacation
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class VacationNotFoundError(LeafEntityNotFoundError):
    """Error raised when a vacation is not found."""


class VacationRepository(LeafEntityRepository[Vacation], abc.ABC):
    """A repository of vacations."""
