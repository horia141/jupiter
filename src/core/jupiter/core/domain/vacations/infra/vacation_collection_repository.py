"""A repository for vacation collections."""
import abc

from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class VacationCollectionRepository(TrunkEntityRepository[VacationCollection], abc.ABC):
    """A repository of vacation collections."""
