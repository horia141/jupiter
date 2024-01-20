"""SQLite based Person repositories."""

from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import (
    PersonRepository,
)
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)


class SqlitePersonCollectionRepository(
    SqliteTrunkEntityRepository[PersonCollection], PersonCollectionRepository
):
    """A repository of Person collections."""


class SqlitePersonRepository(SqliteLeafEntityRepository[Person], PersonRepository):
    """A repository of persons."""
