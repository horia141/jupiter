"""The SQLIte based auth repository."""
from typing import Final

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.infra.auth_repository import (
    AuthNotFoundError,
    AuthRepository,
)
from jupiter.core.domain.auth.password_hash import PasswordHash
from jupiter.core.domain.auth.recovery_token_hash import RecoveryTokenHash
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.secure import secure_class
from jupiter.core.repository.sqlite.infra.events import build_event_table, upsert_events
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
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection


@secure_class
class SqliteAuthRepository(AuthRepository):
    """The SQLite based auth repository."""

    _connection: Final[AsyncConnection]
    _auth_table: Final[Table]
    _auth_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._auth_table = Table(
            "auth",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "user_ref_id",
                Integer,
                ForeignKey("user.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            Column("password_hash", String, nullable=False),
            Column("recovery_token_hash", String, nullable=False),
            keep_existing=True,
        )
        self._auth_event_table = build_event_table(self._auth_table, metadata)

    async def create(self, entity: Auth) -> Auth:
        """Create a auth."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._auth_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                user_ref_id=entity.user_ref_id.as_int(),
                password_hash=entity.password_hash.password_hash_raw,
                recovery_token_hash=entity.recovery_token_hash.token_hash_raw,
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._auth_event_table, entity)
        return entity

    async def save(self, entity: Auth) -> Auth:
        """Save a auth."""
        result = await self._connection.execute(
            update(self._auth_table)
            .where(self._auth_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                user_ref_id=entity.user_ref_id.as_int(),
                password_hash=entity.password_hash.password_hash_raw,
                recovery_token_hash=entity.recovery_token_hash.token_hash_raw,
            )
        )
        if result.rowcount == 0:
            raise AuthNotFoundError(f"Auth with id {entity.ref_id} does not exist")

        await upsert_events(self._connection, self._auth_event_table, entity)
        return entity

    async def load_by_parent(self, parent_ref_id: EntityId) -> Auth:
        """Retrieve a auth by id."""
        query_stmt = select(self._auth_table).where(
            self._auth_table.c.user_ref_id == parent_ref_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise AuthNotFoundError(f"Auth for user {parent_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> Auth:
        return Auth(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            events=[],
            user_ref_id=EntityId.from_raw(str(row["user_ref_id"])),
            password_hash=PasswordHash.from_raw(row["password_hash"]),
            recovery_token_hash=RecoveryTokenHash.from_raw(row["recovery_token_hash"]),
        )
