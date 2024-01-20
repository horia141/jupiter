"""The Email tasks repositories."""

from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_collection_repository import (
    EmailTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_repository import (
    EmailTaskRepository,
)
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)


class SqliteEmailTaskCollectionRepository(
    SqliteTrunkEntityRepository[EmailTaskCollection], EmailTaskCollectionRepository
):
    """The email task collection repository."""


class SqliteEmailTaskRepository(
    SqliteLeafEntityRepository[EmailTask], EmailTaskRepository
):
    """The email task repository."""
