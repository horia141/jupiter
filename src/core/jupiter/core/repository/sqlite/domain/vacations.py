"""The SQLite based vacations repository."""

from jupiter.core.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionRepository,
)
from jupiter.core.domain.vacations.infra.vacation_repository import (
    VacationRepository,
)
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)


class SqliteVacationCollectionRepository(
    SqliteTrunkEntityRepository[VacationCollection], VacationCollectionRepository
):
    """The vacation collection repository."""


class SqliteVacationRepository(
    SqliteLeafEntityRepository[Vacation], VacationRepository
):
    """A repository for vacations."""
