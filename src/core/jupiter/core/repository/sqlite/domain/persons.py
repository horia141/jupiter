"""SQLite based Person repositories."""

from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import (
    PersonRepository,
)
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
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
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Unicode,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqlitePersonCollectionRepository(
    SqliteTrunkEntityRepository[PersonCollection], PersonCollectionRepository
):
    """A repository of Person collections."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "person_collection",
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
                    nullable=False,
                ),
                Column(
                    "catch_up_project_ref_id",
                    Integer,
                    ForeignKey("projct.ref_id"),
                    nullable=True,
                ),
                keep_existing=True,
            ),
        )

    @staticmethod
    def _entity_to_row(entity: PersonCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
            "catch_up_project_ref_id": entity.catch_up_project_ref_id.as_int(),
        }

    @staticmethod
    def _row_to_entity(row: RowType) -> PersonCollection:
        return PersonCollection(
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
            catch_up_project_ref_id=EntityId.from_raw(
                str(row["catch_up_project_ref_id"]),
            ),
        )


class SqlitePersonRepository(SqliteLeafEntityRepository[Person], PersonRepository):
    """A repository of persons."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "person",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "person_collection_ref_id",
                    Integer,
                    ForeignKey("person_collection.ref_id"),
                    nullable=False,
                ),
                Column("name", Unicode(), nullable=False),
                Column("relationship", String(), nullable=False),
                Column("catch_up_period", String, nullable=True),
                Column("catch_up_eisen", String, nullable=True),
                Column("catch_up_difficulty", String, nullable=True),
                Column("catch_up_actionable_from_day", Integer, nullable=True),
                Column("catch_up_actionable_from_month", Integer, nullable=True),
                Column("catch_up_due_at_time", String, nullable=True),
                Column("catch_up_due_at_day", Integer, nullable=True),
                Column("catch_up_due_at_month", Integer, nullable=True),
                Column("birthday", String(), nullable=True),
                keep_existing=True,
            ),
        )

    @staticmethod
    def _entity_to_row(entity: Person) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "person_collection_ref_id": entity.person_collection.as_int(),
            "name": str(entity.name),
            "relationship": entity.relationship.value,
            "catch_up_period": entity.catch_up_params.period.value
            if entity.catch_up_params
            else None,
            "catch_up_eisen": entity.catch_up_params.eisen.value
            if entity.catch_up_params and entity.catch_up_params.eisen
            else None,
            "catch_up_difficulty": entity.catch_up_params.difficulty.value
            if entity.catch_up_params and entity.catch_up_params.difficulty
            else None,
            "catch_up_actionable_from_day": entity.catch_up_params.actionable_from_day.as_int()
            if entity.catch_up_params and entity.catch_up_params.actionable_from_day
            else None,
            "catch_up_actionable_from_month": entity.catch_up_params.actionable_from_month.as_int()
            if entity.catch_up_params and entity.catch_up_params.actionable_from_month
            else None,
            "catch_up_due_at_time": str(entity.catch_up_params.due_at_time)
            if entity.catch_up_params and entity.catch_up_params.due_at_time
            else None,
            "catch_up_due_at_day": entity.catch_up_params.due_at_day.as_int()
            if entity.catch_up_params and entity.catch_up_params.due_at_day
            else None,
            "catch_up_due_at_month": entity.catch_up_params.due_at_month.as_int()
            if entity.catch_up_params and entity.catch_up_params.due_at_month
            else None,
            "birthday": str(entity.birthday) if entity.birthday else None,
        }

    @staticmethod
    def _row_to_entity(row: RowType) -> Person:
        return Person(
            ref_id=EntityId(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            person_collection=ParentLink(
                EntityId.from_raw(
                    str(row["person_collection_ref_id"]),
                )
            ),
            name=PersonName.from_raw(row["name"]),
            relationship=PersonRelationship.from_raw(row["relationship"]),
            catch_up_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(row["catch_up_period"]),
                eisen=Eisen.from_raw(row["catch_up_eisen"])
                if row["catch_up_eisen"]
                else None,
                difficulty=Difficulty.from_raw(row["catch_up_difficulty"])
                if row["catch_up_difficulty"]
                else None,
                actionable_from_day=RecurringTaskDueAtDay(
                    row["catch_up_actionable_from_day"],
                )
                if row["catch_up_actionable_from_day"] is not None
                else None,
                actionable_from_month=RecurringTaskDueAtMonth(
                    row["catch_up_actionable_from_month"],
                )
                if row["catch_up_actionable_from_month"] is not None
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(row["catch_up_due_at_time"])
                if row["catch_up_due_at_time"] is not None
                else None,
                due_at_day=RecurringTaskDueAtDay(row["catch_up_due_at_day"])
                if row["catch_up_due_at_day"] is not None
                else None,
                due_at_month=RecurringTaskDueAtMonth(row["catch_up_due_at_month"])
                if row["catch_up_due_at_month"] is not None
                else None,
            )
            if row["catch_up_period"] is not None
            else None,
            birthday=PersonBirthday.from_raw(row["birthday"])
            if row["birthday"]
            else None,
        )
