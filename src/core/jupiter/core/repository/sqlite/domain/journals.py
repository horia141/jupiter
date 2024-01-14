"""The SQLite based journals repository."""

from typing import cast

import pydantic
from jupiter.core.domain.core.adate import ADate
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
from jupiter.core.domain.journals.journal_source import JournalSource
from jupiter.core.domain.report.report_period_result import ReportPeriodResult
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
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
    Date,
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
            Table(
                "journal_collection",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "workspace_ref_id",
                    Integer,
                    ForeignKey("workspace.ref_id"),
                    unique=True,
                    index=True,
                    nullable=False,
                ),
                Column("periods", JSON, nullable=False),
                Column(
                    "writing_task_project_ref_id",
                    Integer,
                    ForeignKey("project.ref_id"),
                    nullable=False,
                ),
                Column("writing_task_eisen", String, nullable=False),
                Column("writing_task_difficulty", String, nullable=False),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: JournalCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
            "periods": [period.value for period in entity.periods],
            "writing_task_project_ref_id": entity.writing_task_project_ref_id.as_int(),
            "writing_task_eisen": cast(Eisen, entity.writing_task_gen_params.eisen),
            "writing_task_difficulty": cast(
                Difficulty, entity.writing_task_gen_params.difficulty
            ),
        }

    def _row_to_entity(self, row: RowType) -> JournalCollection:
        return JournalCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace=ParentLink(EntityId.from_raw(str(row["workspace_ref_id"]))),
            periods=set(RecurringTaskPeriod(period) for period in row["periods"]),
            writing_task_project_ref_id=EntityId.from_raw(
                str(row["writing_task_project_ref_id"])
            ),
            writing_task_gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.DAILY,
                eisen=Eisen(row["writing_task_eisen"]),
                difficulty=Difficulty(row["writing_task_difficulty"]),
            ),
        )


_ValidatedReportPeriodResult = pydantic.dataclasses.dataclass(ReportPeriodResult)


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
            Table(
                "journal",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "journal_collection_ref_id",
                    Integer,
                    ForeignKey("journal_collection.ref_id"),
                    nullable=False,
                ),
                Column("name", String(100), nullable=False),
                Column("source", String, nullable=False),
                Column("right_now", Date, nullable=False),
                Column("period", String, nullable=False),
                Column("timeline", String, nullable=False),
                Column("report", JSON, nullable=False),
                keep_existing=True,
            ),
            already_exists_err_cls=JournalExistsForDatePeriodCombinationError,
        )

    def _entity_to_row(self, entity: Journal) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "journal_collection_ref_id": entity.journal_collection.as_int(),
            "name": str(entity.name),
            "source": entity.source.value,
            "right_now": entity.right_now.to_db(),
            "period": entity.period.value,
            "timeline": entity.timeline,
            "report": entity.report,  # JSON serialisation at engine-level via pydantic does the trick
        }

    def _row_to_entity(self, row: RowType) -> Journal:
        return Journal(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            journal_collection=ParentLink(
                EntityId.from_raw(
                    str(row["journal_collection_ref_id"]),
                )
            ),
            name=EntityName.from_raw(row["name"]),
            source=JournalSource(row["source"]),
            right_now=ADate.from_db(row["right_now"]),
            period=RecurringTaskPeriod(row["period"]),
            timeline=row["timeline"],
            report=cast(
                ReportPeriodResult, _ValidatedReportPeriodResult(**row["report"])
            ),  # JSON serialisation at engine-level via pydantic does the trick
        )
