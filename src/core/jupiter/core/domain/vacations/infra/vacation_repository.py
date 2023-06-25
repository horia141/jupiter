"""A repository of vacations."""
import abc

from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class VacationNotFoundError(LeafEntityNotFoundError):
    """Error raised when a vacation is not found."""


class VacationRepository(LeafEntityRepository[Vacation], abc.ABC):
    """A repository of vacations."""
