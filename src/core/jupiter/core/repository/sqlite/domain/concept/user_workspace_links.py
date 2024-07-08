"""The SQLIte based user workspace links repository."""

from jupiter.core.domain.concept.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
    UserWorkspaceLinkRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.repository.sqlite.infra.repository import SqliteRootEntityRepository
from sqlalchemy import (
    select,
)


class SqliteUserWorkspaceLinkRepository(
    SqliteRootEntityRepository[UserWorkspaceLink], UserWorkspaceLinkRepository
):
    """The SQLite based user workspace links repository."""

    async def load_by_user(self, user_id: EntityId) -> UserWorkspaceLink:
        """Load the user workspace link for a particular user."""
        query_stmt = select(self._table).where(
            self._table.c.user_ref_id == user_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"User workspace link for user with id {user_id} does not exist"
            )
        return self._row_to_entity(result)
