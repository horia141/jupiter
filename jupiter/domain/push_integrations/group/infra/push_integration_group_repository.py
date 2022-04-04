"""A repository of push integrations groups."""
import abc

from jupiter.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import (
    TrunkEntityRepository,
    TrunkEntityNotFoundError,
    TrunkEntityAlreadyExistsError,
)


class PushIntegrationGroupAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a push integration already exists."""


class PushIntegrationGroupNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a push integration is not found."""


class PushIntegrationGroupRepository(
    TrunkEntityRepository[PushIntegrationGroup], abc.ABC
):
    """A repository of push integrations."""

    @abc.abstractmethod
    def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> PushIntegrationGroup:
        """Retrieve a push integration group by its id."""
