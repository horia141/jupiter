"""The push integration group repository SQLite implementation."""

from jupiter.core.domain.push_integrations.group.infra.push_integration_group_repository import (
    PushIntegrationGroupRepository,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.repository.sqlite.infra.repository import SqliteTrunkEntityRepository


class SqlitePushIntegrationGroupRepository(
    SqliteTrunkEntityRepository[PushIntegrationGroup], PushIntegrationGroupRepository
):
    """The push integration group repository SQLite implementation."""
