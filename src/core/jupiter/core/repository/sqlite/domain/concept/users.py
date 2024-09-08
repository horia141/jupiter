"""The SQLIte based user repository."""

from jupiter.core.domain.concept.user.user import (
    User,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepository,
)
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.repository.sqlite.infra.repository import SqliteRootEntityRepository
from sqlalchemy import (
    MetaData,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteUserRepository(SqliteRootEntityRepository[User], UserRepository):
    """The SQLite based user repository."""

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
