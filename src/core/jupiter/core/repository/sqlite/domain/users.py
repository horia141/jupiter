"""The SQLIte based user repository."""
from typing import Final, Iterable

from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.features import UserFeature
from jupiter.core.domain.timezone import Timezone
from jupiter.core.domain.user.avatar import Avatar
from jupiter.core.domain.user.infra.user_repository import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepository,
)
from jupiter.core.domain.user.user import User
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.events import build_event_table, upsert_events
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
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteUserRepository(UserRepository):
    """The SQLite based user repository."""

    _connection: Final[AsyncConnection]
    _user_table: Final[Table]
    _user_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._user_table = Table(
            "user",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "email_address", String(100), index=True, unique=True, nullable=False
            ),
            Column("name", String(100), nullable=False),
            Column("avatar", String, nullable=False),
            Column("timezone", String(100), nullable=False),
            Column("feature_flags", JSON, nullable=False),
            keep_existing=True,
        )
        self._user_event_table = build_event_table(self._user_table, metadata)

    async def create(self, entity: User) -> User:
        """Create a user."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._user_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    email_address=str(entity.email_address),
                    name=str(entity.name),
                    avatar=entity.avatar.avatar_as_data_url,
                    timezone=str(entity.timezone),
                    feature_flags={f.value: v for f, v in entity.feature_flags.items()},
                )
            )
        except IntegrityError as err:
            raise UserAlreadyExistsError(
                f"User with email address {entity.email_address} already exists"
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._user_event_table, entity)
        return entity

    async def save(self, entity: User) -> User:
        """Save a user."""
        result = await self._connection.execute(
            update(self._user_table)
            .where(self._user_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                email_address=str(entity.email_address),
                name=str(entity.name),
                avatar=entity.avatar.avatar_as_data_url,
                timezone=str(entity.timezone),
                feature_flags={f.value: v for f, v in entity.feature_flags.items()},
            )
        )
        if result.rowcount == 0:
            raise UserNotFoundError(f"User with id {entity.ref_id} does not exist")

        await upsert_events(self._connection, self._user_event_table, entity)
        return entity

    async def load_by_id(self, entity_id: EntityId) -> User:
        """Retrieve a user by id."""
        query_stmt = select(self._user_table).where(
            self._user_table.c.ref_id == entity_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise UserNotFoundError(f"User with id {entity_id} does not exist")
        return self._row_to_entity(result)

    async def load_optional(self, entity_id: EntityId) -> User | None:
        """Retrieve a user by id and return None if it does not exist."""
        query_stmt = select(self._user_table).where(
            self._user_table.c.ref_id == entity_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def load_by_email_address(self, email_address: EmailAddress) -> User:
        """Retrieve a user by their email address."""
        query_stmt = select(self._user_table).where(
            self._user_table.c.email_address == str(email_address)
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise UserNotFoundError(f"User with email {email_address} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[User]:
        """Find all users matching some criteria."""
        query_stmt = select(self._user_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._user_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._user_table.c.ref_id.in_(
                    [ref_id.as_int() for ref_id in filter_ref_ids]
                )
            )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

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
