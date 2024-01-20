"""The SQLite based journals repository."""

from typing import cast

import pydantic
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.journals.infra.journal_collection_repository import (
    JournalCollectionRepository,
)
from jupiter.core.domain.journals.infra.journal_repository import (
    JournalExistsForDatePeriodCombinationError,
    JournalRepository,
)
from jupiter.core.domain.journals.journal import Journal
from jupiter.core.domain.journals.journal_collection import JournalCollection
from jupiter.core.domain.report.report_period_result import ReportPeriodResult
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
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
