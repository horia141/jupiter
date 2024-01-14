"""The SQLIte based auth repository."""

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.infra.auth_repository import (
    AuthRepository,
)
from jupiter.core.domain.auth.password_hash import PasswordHash
from jupiter.core.domain.auth.recovery_token_hash import RecoveryTokenHash
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.secure import secure_class
from jupiter.core.repository.sqlite.infra.repository import SqliteStubEntityRepository
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
)
from sqlalchemy.ext.asyncio import AsyncConnection


@secure_class
class SqliteAuthRepository(SqliteStubEntityRepository[Auth], AuthRepository):
    """The SQLite based auth repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    def _entity_to_row(self, entity: Auth) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "user_ref_id": entity.user.as_int(),
            "password_hash": entity.password_hash.password_hash_raw,
            "recovery_token_hash": entity.recovery_token_hash.token_hash_raw,
        }

    def _row_to_entity(self, row: RowType) -> Auth:
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
            user=ParentLink(EntityId.from_raw(str(row["user_ref_id"]))),
            password_hash=PasswordHash.from_raw(row["password_hash"]),
            recovery_token_hash=RecoveryTokenHash.from_raw(row["recovery_token_hash"]),
        )
