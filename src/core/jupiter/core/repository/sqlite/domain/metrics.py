"""SQLite based metrics repositories."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import (
    MetricRepository,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteBranchEntityRepository,
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Unicode,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteMetricCollectionRepository(
    SqliteTrunkEntityRepository[MetricCollection], MetricCollectionRepository
):
    """The metric collection repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "metric_collection",
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
                Column(
                    "collection_project_ref_id",
                    Integer,
                    ForeignKey("project.ref_id"),
                    nullable=False,
                ),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: MetricCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
            "collection_project_ref_id": entity.collection_project_ref_id.as_int(),
        }

    def _row_to_entity(self, row: RowType) -> MetricCollection:
        return MetricCollection(
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
            collection_project_ref_id=EntityId.from_raw(
                str(row["collection_project_ref_id"]),
            ),
        )


class SqliteMetricRepository(SqliteBranchEntityRepository[Metric], MetricRepository):
    """A repository for metrics."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "metric",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "metric_collection_ref_id",
                    Integer,
                    ForeignKey("metric_collection.ref_id"),
                    nullable=False,
                ),
                Column("name", Unicode(), nullable=False),
                Column("icon", String(1), nullable=True),
                Column("collection_period", String, nullable=True),
                Column("collection_eisen", String, nullable=True),
                Column("collection_difficulty", String, nullable=True),
                Column("collection_actionable_from_day", Integer, nullable=True),
                Column("collection_actionable_from_month", Integer, nullable=True),
                Column("collection_due_at_time", String, nullable=True),
                Column("collection_due_at_day", Integer, nullable=True),
                Column("collection_due_at_month", Integer, nullable=True),
                Column("metric_unit", String(), nullable=True),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: Metric) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "metric_collection_ref_id": entity.metric_collection.as_int(),
            "name": str(entity.name),
            "icon": entity.icon.to_safe() if entity.icon else None,
            "collection_period": entity.collection_params.period.value
            if entity.collection_params
            else None,
            "collection_eisen": entity.collection_params.eisen.value
            if entity.collection_params and entity.collection_params.eisen
            else None,
            "collection_difficulty": entity.collection_params.difficulty.value
            if entity.collection_params and entity.collection_params.difficulty
            else None,
            "collection_actionable_from_day": entity.collection_params.actionable_from_day.as_int()
            if entity.collection_params and entity.collection_params.actionable_from_day
            else None,
            "collection_actionable_from_month": entity.collection_params.actionable_from_month.as_int()
            if entity.collection_params
            and entity.collection_params.actionable_from_month
            else None,
            "collection_due_at_time": str(entity.collection_params.due_at_time)
            if entity.collection_params and entity.collection_params.due_at_time
            else None,
            "collection_due_at_day": entity.collection_params.due_at_day.as_int()
            if entity.collection_params and entity.collection_params.due_at_day
            else None,
            "collection_due_at_month": entity.collection_params.due_at_month.as_int()
            if entity.collection_params and entity.collection_params.due_at_month
            else None,
            "metric_unit": entity.metric_unit.value if entity.metric_unit else None,
        }

    def _row_to_entity(self, row: RowType) -> Metric:
        return Metric(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            metric_collection=ParentLink(
                EntityId.from_raw(
                    str(row["metric_collection_ref_id"]),
                )
            ),
            name=MetricName.from_raw(row["name"]),
            icon=EntityIcon.from_safe(row["icon"]) if row["icon"] else None,
            collection_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(row["collection_period"]),
                eisen=Eisen.from_raw(row["collection_eisen"])
                if row["collection_eisen"]
                else None,
                difficulty=Difficulty.from_raw(row["collection_difficulty"])
                if row["collection_difficulty"]
                else None,
                actionable_from_day=RecurringTaskDueAtDay(
                    row["collection_actionable_from_day"],
                )
                if row["collection_actionable_from_day"] is not None
                else None,
                actionable_from_month=RecurringTaskDueAtMonth(
                    row["collection_actionable_from_month"],
                )
                if row["collection_actionable_from_month"] is not None
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(
                    row["collection_due_at_time"],
                )
                if row["collection_due_at_time"] is not None
                else None,
                due_at_day=RecurringTaskDueAtDay(row["collection_due_at_day"])
                if row["collection_due_at_day"] is not None
                else None,
                due_at_month=RecurringTaskDueAtMonth(row["collection_due_at_month"])
                if row["collection_due_at_month"] is not None
                else None,
            )
            if row["collection_period"] is not None
            else None,
            metric_unit=MetricUnit.from_raw(row["metric_unit"])
            if row["metric_unit"]
            else None,
        )


class SqliteMetricEntryRepository(
    SqliteLeafEntityRepository[MetricEntry], MetricEntryRepository
):
    """A repository of metric entries."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "metric_entry",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "metric_ref_id",
                    ForeignKey("metric.ref_id"),
                    index=True,
                    nullable=False,
                ),
                Column("collection_time", DateTime, nullable=False),
                Column("value", Float, nullable=False),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: MetricEntry) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "metric_ref_id": entity.metric.as_int(),
            "collection_time": entity.collection_time.to_db(),
            "value": entity.value,
        }

    def _row_to_entity(self, row: RowType) -> MetricEntry:
        return MetricEntry(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=MetricEntry.build_name(
                ADate.from_db(row["collection_time"]), row["value"]
            ),
            metric=ParentLink(EntityId.from_raw(str(row["metric_ref_id"]))),
            collection_time=ADate.from_db(row["collection_time"]),
            value=row["value"],
        )
