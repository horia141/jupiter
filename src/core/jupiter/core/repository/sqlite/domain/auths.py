"""The SQLIte based auth repository."""

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.infra.auth_repository import (
    AuthRepository,
)
from jupiter.core.framework.secure import secure_class
from jupiter.core.repository.sqlite.infra.repository import SqliteStubEntityRepository


@secure_class
class SqliteAuthRepository(SqliteStubEntityRepository[Auth], AuthRepository):
    """The SQLite based auth repository."""
