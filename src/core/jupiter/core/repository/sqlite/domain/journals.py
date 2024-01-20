"""The SQLite based journals repository."""


from jupiter.core.domain.journals.infra.journal_collection_repository import (
    JournalCollectionRepository,
)
from jupiter.core.domain.journals.infra.journal_repository import (
    JournalExistsForDatePeriodCombinationError,
    JournalRepository,
)
from jupiter.core.domain.journals.journal import Journal
from jupiter.core.domain.journals.journal_collection import JournalCollection
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    MetaData,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteJournalCollectionRepository(
    SqliteTrunkEntityRepository[JournalCollection], JournalCollectionRepository
):
    """The journal collection repository."""


class SqliteJournalRepository(SqliteLeafEntityRepository[Journal], JournalRepository):
    """A repository for journals."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            already_exists_err_cls=JournalExistsForDatePeriodCombinationError,
        )
