"""A repository of vacations."""
import abc

from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class VacationRepository(LeafEntityRepository[Vacation], abc.ABC):
    """A repository of vacations."""
