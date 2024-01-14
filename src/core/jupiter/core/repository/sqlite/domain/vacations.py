"""The SQLite based vacations repository."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionRepository,
)
from jupiter.core.domain.vacations.infra.vacation_repository import (
    VacationRepository,
)
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
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


class SqliteVacationCollectionRepository(
    SqliteTrunkEntityRepository[VacationCollection], VacationCollectionRepository
):
    """The vacation collection repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "vacation_collection",
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
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: VacationCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
        }

    def _row_to_entity(self, row: RowType) -> VacationCollection:
        return VacationCollection(
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
        )


class SqliteVacationRepository(
    SqliteLeafEntityRepository[Vacation], VacationRepository
):
    """A repository for vacations."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "vacation",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "vacation_collection_ref_id",
                    Integer,
                    ForeignKey("vacation_collection.ref_id"),
                    nullable=False,
                ),
                Column("name", String(100), nullable=False),
                Column("start_date", Date, nullable=False),
                Column("end_date", Date, nullable=False),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: Vacation) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "vacation_collection_ref_id": entity.vacation_collection.as_int(),
            "name": str(entity.name),
            "start_date": entity.start_date.to_db(),
            "end_date": entity.end_date.to_db(),
        }

    def _row_to_entity(self, row: RowType) -> Vacation:
        return Vacation(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            vacation_collection=ParentLink(
                EntityId.from_raw(
                    str(row["vacation_collection_ref_id"]),
                )
            ),
            name=VacationName.from_raw(row["name"]),
            start_date=ADate.from_db(row["start_date"]),
            end_date=ADate.from_db(row["end_date"]),
        )
