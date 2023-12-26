"""SQLite based Person repositories."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionNotFoundError,
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import (
    PersonAlreadyExistsError,
    PersonNotFoundError,
    PersonRepository,
)
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import EntityLinkFilterCompiled
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
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
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqlitePersonCollectionRepository(PersonCollectionRepository):
    """A repository of Person collections."""

    _connection: Final[AsyncConnection]
    _person_collection_table: Final[Table]
    _person_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._person_collection_table = Table(
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
            Column("catch_up_project_ref_id", Integer, nullable=True),
            keep_existing=True,
        )
        self._person_collection_event_table = build_event_table(
            self._person_collection_table,
            metadata,
        )

    async def create(self, entity: PersonCollection) -> PersonCollection:
        """Create a Person."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._person_collection_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
                catch_up_project_ref_id=entity.catch_up_project_ref_id.as_int(),
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._person_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: PersonCollection) -> PersonCollection:
        """Save a Person - it should already exist."""
        result = await self._connection.execute(
            update(self._person_collection_table)
            .where(self._person_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
                catch_up_project_ref_id=entity.catch_up_project_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise PersonCollectionNotFoundError("The Person does not exist")
        await upsert_events(
            self._connection,
            self._person_collection_event_table,
            entity,
        )
        return entity

    async def load_by_parent(self, parent_ref_id: EntityId) -> PersonCollection:
        """Load the Person."""
        query_stmt = select(self._person_collection_table).where(
            self._person_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise PersonCollectionNotFoundError(
                f"Person collection for workspace {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

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
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])),
            catch_up_project_ref_id=EntityId.from_raw(
                str(row["catch_up_project_ref_id"]),
            ),
        )


class SqlitePersonRepository(PersonRepository):
    """A repository of persons."""

    _connection: Final[AsyncConnection]
    _person_table: Final[Table]
    _person_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._person_table = Table(
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
        )
        self._person_event_table = build_event_table(self._person_table, metadata)

    async def create(self, entity: Person) -> Person:
        """Create a person."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._person_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    person_collection_ref_id=entity.person_collection_ref_id.as_int(),
                    name=str(entity.name),
                    relationship=entity.relationship.value,
                    catch_up_period=entity.catch_up_params.period.value
                    if entity.catch_up_params
                    else None,
                    catch_up_eisen=entity.catch_up_params.eisen.value
                    if entity.catch_up_params and entity.catch_up_params.eisen
                    else None,
                    catch_up_difficulty=entity.catch_up_params.difficulty.value
                    if entity.catch_up_params and entity.catch_up_params.difficulty
                    else None,
                    catch_up_actionable_from_day=entity.catch_up_params.actionable_from_day.as_int()
                    if entity.catch_up_params
                    and entity.catch_up_params.actionable_from_day
                    else None,
                    catch_up_actionable_from_month=entity.catch_up_params.actionable_from_month.as_int()
                    if entity.catch_up_params
                    and entity.catch_up_params.actionable_from_month
                    else None,
                    catch_up_due_at_time=str(entity.catch_up_params.due_at_time)
                    if entity.catch_up_params and entity.catch_up_params.due_at_time
                    else None,
                    catch_up_due_at_day=entity.catch_up_params.due_at_day.as_int()
                    if entity.catch_up_params and entity.catch_up_params.due_at_day
                    else None,
                    catch_up_due_at_month=entity.catch_up_params.due_at_month.as_int()
                    if entity.catch_up_params and entity.catch_up_params.due_at_month
                    else None,
                    birthday=str(entity.birthday) if entity.birthday else None,
                ),
            )
        except IntegrityError as err:
            raise PersonAlreadyExistsError(
                f"Person with name {entity.name} already exists",
            ) from err
        entity = entity.assign_ref_id(
            EntityId.from_raw(str(result.inserted_primary_key[0])),
        )
        await upsert_events(self._connection, self._person_event_table, entity)
        return entity

    async def save(self, entity: Person) -> Person:
        """Save a person - it should already exist."""
        result = await self._connection.execute(
            update(self._person_table)
            .where(self._person_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                person_collection_ref_id=entity.person_collection_ref_id.as_int(),
                name=str(entity.name),
                relationship=entity.relationship.value,
                catch_up_period=entity.catch_up_params.period.value
                if entity.catch_up_params
                else None,
                catch_up_eisen=entity.catch_up_params.eisen.value
                if entity.catch_up_params and entity.catch_up_params.eisen
                else None,
                catch_up_difficulty=entity.catch_up_params.difficulty.value
                if entity.catch_up_params and entity.catch_up_params.difficulty
                else None,
                catch_up_actionable_from_day=entity.catch_up_params.actionable_from_day.as_int()
                if entity.catch_up_params and entity.catch_up_params.actionable_from_day
                else None,
                catch_up_actionable_from_month=entity.catch_up_params.actionable_from_month.as_int()
                if entity.catch_up_params
                and entity.catch_up_params.actionable_from_month
                else None,
                catch_up_due_at_time=str(entity.catch_up_params.due_at_time)
                if entity.catch_up_params and entity.catch_up_params.due_at_time
                else None,
                catch_up_due_at_day=entity.catch_up_params.due_at_day.as_int()
                if entity.catch_up_params and entity.catch_up_params.due_at_day
                else None,
                catch_up_due_at_month=entity.catch_up_params.due_at_month.as_int()
                if entity.catch_up_params and entity.catch_up_params.due_at_month
                else None,
                birthday=str(entity.birthday) if entity.birthday else None,
            ),
        )
        if result.rowcount == 0:
            raise PersonNotFoundError(
                f"A person with id {entity.ref_id} does not exist",
            )
        await upsert_events(self._connection, self._person_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Person:
        """Find a person by id."""
        query_stmt = select(self._person_table).where(
            self._person_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._person_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise PersonNotFoundError(f"Person identified by {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Person]:
        """Find all person matching some criteria."""
        query_stmt = select(self._person_table).where(
            self._person_table.c.person_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._person_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._person_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[Person]:
        """Find all big plans with generic filters."""
        query_stmt = select(self._person_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._person_table.c.archived.is_(False))

        query_stmt = compile_query_relative_to(query_stmt, self._person_table, kwargs)

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Person:
        """Hard remove a person - an irreversible operation."""
        query_stmt = select(self._person_table).where(
            self._person_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise PersonNotFoundError(f"Person identified by {ref_id} does not exist")
        await self._connection.execute(
            delete(self._person_table).where(
                self._person_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._person_event_table, ref_id)
        return self._row_to_entity(result)

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
            person_collection_ref_id=EntityId.from_raw(
                str(row["person_collection_ref_id"]),
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
