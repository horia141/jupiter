"""A repository of push integrations groups."""
import abc

from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class PushIntegrationGroupRepository(
    TrunkEntityRepository[PushIntegrationGroup],
    abc.ABC,
):
    """A repository of push integrations."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> PushIntegrationGroup:
        """Retrieve a push integration group by its id."""
