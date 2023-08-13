"""The Email tasks repositories."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.email.infra.email_task_collection_repository import (
    EmailTaskCollectionAlreadyExistsError,
    EmailTaskCollectionNotFoundError,
    EmailTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_repository import (
    EmailTaskNotFoundError,
    EmailTaskRepository,
)
from jupiter.core.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
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
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteEmailTaskCollectionRepository(EmailTaskCollectionRepository):
    """The email task collection repository."""

    _connection: Final[AsyncConnection]
    _email_task_collection_table: Final[Table]
    _email_task_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._email_task_collection_table = Table(
            "email_task_collection",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "push_integration_group_ref_id",
                Integer,
                ForeignKey("push_integration_group_ref_id.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            Column(
                "generation_project_ref_id",
                Integer,
                ForeignKey("project.ref_id"),
                nullable=False,
            ),
            keep_existing=True,
        )
        self._email_task_collection_event_table = build_event_table(
            self._email_task_collection_table,
            metadata,
        )

    async def create(self, entity: EmailTaskCollection) -> EmailTaskCollection:
        """Create a email task collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._email_task_collection_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    push_integration_group_ref_id=entity.push_integration_group_ref_id.as_int(),
                    generation_project_ref_id=entity.generation_project_ref_id.as_int(),
                ),
            )
        except IntegrityError as err:
            raise EmailTaskCollectionAlreadyExistsError(
                f"EmailTask collection for push integration group {entity.push_integration_group_ref_id} "
                + "already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._email_task_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: EmailTaskCollection) -> EmailTaskCollection:
        """Save a email task collection."""
        result = await self._connection.execute(
            update(self._email_task_collection_table)
            .where(self._email_task_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                push_integration_group_ref_id=entity.push_integration_group_ref_id.as_int(),
                generation_project_ref_id=entity.generation_project_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise EmailTaskCollectionNotFoundError(
                "The email task collection does not exist",
            )
        await upsert_events(
            self._connection,
            self._email_task_collection_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> EmailTaskCollection:
        """Retrieve a email task collection."""
        query_stmt = select(self._email_task_collection_table).where(
            self._email_task_collection_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._email_task_collection_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EmailTaskCollectionNotFoundError(
                f"EmailTask collection with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> EmailTaskCollection:
        """Retrieve a email task collection for a project."""
        query_stmt = select(self._email_task_collection_table).where(
            self._email_task_collection_table.c.push_integration_group_ref_id
            == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EmailTaskCollectionNotFoundError(
                f"EmailTask collection for push integration group {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> EmailTaskCollection:
        return EmailTaskCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            push_integration_group_ref_id=EntityId.from_raw(
                str(row["push_integration_group_ref_id"]),
            ),
            generation_project_ref_id=EntityId.from_raw(
                str(row["generation_project_ref_id"]),
            ),
        )


class SqliteEmailTaskRepository(EmailTaskRepository):
    """The email task repository."""

    _connection: Final[AsyncConnection]
    _email_task_table: Final[Table]
    _email_task_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._email_task_table = Table(
            "email_task",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "email_task_collection_ref_id",
                Integer,
                ForeignKey("email_task_collection.ref_id"),
                nullable=False,
            ),
            Column("from_address", String(), nullable=False),
            Column("from_name", String(), nullable=False),
            Column("to_address", String(), nullable=False),
            Column("subject", String(), nullable=False),
            Column("body", String(), nullable=False),
            Column("generation_extra_info", String(), nullable=False),
            Column("has_generated_task", Boolean, nullable=False),
            keep_existing=True,
        )
        self._email_task_event_table = build_event_table(
            self._email_task_table,
            metadata,
        )

    async def create(self, entity: EmailTask) -> EmailTask:
        """Create the email task."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._email_task_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                email_task_collection_ref_id=entity.email_task_collection_ref_id.as_int(),
                from_address=str(entity.from_address),
                from_name=str(entity.from_name),
                to_address=str(entity.to_address),
                subject=entity.subject,
                body=entity.body,
                generation_extra_info=entity.generation_extra_info.to_db(),
                has_generated_task=entity.has_generated_task,
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._email_task_event_table, entity)
        return entity

    async def save(self, entity: EmailTask) -> EmailTask:
        """Save the email task."""
        result = await self._connection.execute(
            update(self._email_task_table)
            .where(self._email_task_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                email_task_collection_ref_id=entity.email_task_collection_ref_id.as_int(),
                from_address=str(entity.from_address),
                from_name=str(entity.from_name),
                to_address=str(entity.to_address),
                subject=entity.subject,
                body=entity.body,
                generation_extra_info=entity.generation_extra_info.to_db(),
                has_generated_task=entity.has_generated_task,
            ),
        )
        if result.rowcount == 0:
            raise EmailTaskNotFoundError(
                f"Email task with id {entity.ref_id} does not exist",
            )
        await upsert_events(self._connection, self._email_task_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> EmailTask:
        """Retrieve the email task."""
        query_stmt = select(self._email_task_table).where(
            self._email_task_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._email_task_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EmailTaskNotFoundError(f"Big plan with id {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[EmailTask]:
        """Find all the email tasks."""
        query_stmt = select(self._email_task_table).where(
            self._email_task_table.c.email_task_collection_ref_id
            == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._email_task_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._email_task_table.c.ref_id.in_(
                    fi.as_int() for fi in filter_ref_ids
                ),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> EmailTask:
        """Remove a bit plan."""
        query_stmt = select(self._email_task_table).where(
            self._email_task_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EmailTaskNotFoundError(f"Big plan with id {ref_id} does not exist")
        await self._connection.execute(
            delete(self._email_task_table).where(
                self._email_task_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._email_task_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> EmailTask:
        return EmailTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=EmailTask.build_name(
                EmailAddress.from_raw(row["from_address"]),
                EmailUserName.from_raw(row["from_name"]),
                row["subject"],
            ),
            email_task_collection_ref_id=EntityId.from_raw(
                str(row["email_task_collection_ref_id"]),
            ),
            from_address=EmailAddress.from_raw(row["from_address"]),
            from_name=EmailUserName.from_raw(row["from_name"]),
            to_address=EmailAddress.from_raw(row["to_address"]),
            subject=row["subject"],
            body=row["body"],
            generation_extra_info=PushGenerationExtraInfo.from_db(
                row["generation_extra_info"],
            ),
            has_generated_task=row["has_generated_task"],
        )
