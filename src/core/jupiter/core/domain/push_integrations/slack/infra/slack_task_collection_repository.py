"""A repository of slack tasks collections."""
import abc

from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityAlreadyExistsError,
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class SlackTaskCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a slack task collection already exists."""


class SlackTaskCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a slack task collection is not found."""


class SlackTaskCollectionRepository(
    TrunkEntityRepository[SlackTaskCollection],
    abc.ABC,
):
    """A repository of slack task collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> SlackTaskCollection:
        """Retrieve a Slack task collection by its id."""
