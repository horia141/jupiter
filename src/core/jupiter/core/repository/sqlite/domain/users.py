"""The SQLIte based user repository."""

from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.features import UserFeature
from jupiter.core.domain.user.avatar import Avatar
from jupiter.core.domain.user.infra.user_repository import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepository,
)
from jupiter.core.domain.user.user import User
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.repository import SqliteRootEntityRepository
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteUserRepository(SqliteRootEntityRepository[User], UserRepository):
    """The SQLite based user repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "user",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "email_address",
                    String(100),
                    index=True,
                    unique=True,
                    nullable=False,
                ),
                Column("name", String(100), nullable=False),
                Column("avatar", String, nullable=False),
                Column("timezone", String(100), nullable=False),
                Column("feature_flags", JSON, nullable=False),
                keep_existing=True,
            ),
            already_exists_err_cls=UserAlreadyExistsError,
            not_found_err_cls=UserNotFoundError,
        )

    async def load_by_email_address(self, email_address: EmailAddress) -> User:
        """Retrieve a user by their email address."""
        query_stmt = select(self._table).where(
            self._table.c.email_address == str(email_address)
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise UserNotFoundError(f"User with email {email_address} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _entity_to_row(entity: User) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "email_address": str(entity.email_address),
            "name": str(entity.name),
            "avatar": entity.avatar.avatar_as_data_url,
            "timezone": str(entity.timezone),
            "feature_flags": {f.value: v for f, v in entity.feature_flags.items()},
        }

    @staticmethod
    def _row_to_entity(row: RowType) -> User:
        return User(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            events=[],
            email_address=EmailAddress.from_raw(row["email_address"]),
            name=UserName.from_raw(row["name"]),
            avatar=Avatar.from_raw(row["avatar"]),
            timezone=Timezone.from_raw(row["timezone"]),
            feature_flags={UserFeature(f): v for f, v in row["feature_flags"].items()},
        )
